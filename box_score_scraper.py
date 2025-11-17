"""
Box Score Scraper for TBBAS
Scrapes game results and box scores from various sources
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import logging
from models import db, BoxScore
from school_name_normalizer import SchoolNameNormalizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MaxPrepsBoxScoreScraper:
    """Scraper for MaxPreps game results and rankings"""

    BASE_URL = "https://www.maxpreps.com"
    TX_BASKETBALL_URL = "https://www.maxpreps.com/tx/basketball/"
    RANKINGS_URL_TEMPLATE = "https://www.maxpreps.com/tx/association/{association}/basketball/rankings/1/"

    # MaxPreps association mappings
    ASSOCIATIONS = {
        'UIL': 'texas-university-interscholastic-league',
        'TAPPS': 'texas-association-of-private-and-parochial-schools',
        'SPC': 'texas-southwest-prep'
    }

    def __init__(self, use_selenium=False):
        self.use_selenium = use_selenium
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.normalizer = SchoolNameNormalizer()

    def get_selenium_driver(self):
        """Initialize Selenium WebDriver (headless)"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager

            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            return driver

        except Exception as e:
            logger.error(f"Error initializing Selenium: {e}")
            logger.info("Falling back to requests-only mode")
            return None

    def scrape_maxpreps_rankings(self, association='UIL'):
        """
        Scrape rankings from MaxPreps for a specific association
        Returns team rankings with records
        """
        logger.info(f"Scraping MaxPreps {association} rankings...")

        rankings = {}

        try:
            assoc_id = self.ASSOCIATIONS.get(association)
            if not assoc_id:
                logger.error(f"Unknown association: {association}")
                return rankings

            url = self.RANKINGS_URL_TEMPLATE.format(association=assoc_id)

            # Try with requests first
            response = self.session.get(url, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # MaxPreps typically has rankings in JSON or structured HTML
                # Look for team names, records, and rankings

                # This is a simplified parser - MaxPreps structure may vary
                teams_data = []

                # Try to find ranking elements
                # MaxPreps often uses specific classes for rankings
                ranking_elements = soup.find_all(class_=re.compile(r'(rank|team|row)', re.I))

                if ranking_elements:
                    logger.info(f"Found {len(ranking_elements)} potential ranking elements")
                    # Parse the elements to extract team data
                    # This would need to be customized based on actual MaxPreps HTML structure

                logger.info(f"MaxPreps {association} rankings scraped: {len(teams_data)} teams found")

                return teams_data
            else:
                logger.warning(f"MaxPreps returned status {response.status_code}")

        except Exception as e:
            logger.error(f"Error scraping MaxPreps rankings: {e}")

        return rankings

    def scrape_daily_scores(self, target_date=None):
        """
        Scrape game scores for a specific date from MaxPreps
        URL format: https://www.maxpreps.com/tx/basketball/scores/?date=MM/DD/YYYY

        Args:
            target_date: datetime object or None (uses yesterday if None)

        Returns:
            List of game dictionaries
        """
        if target_date is None:
            target_date = datetime.now() - timedelta(days=1)

        date_str = target_date.strftime('%m/%d/%Y')
        url = f"https://www.maxpreps.com/tx/basketball/scores/?date={date_str}"

        logger.info(f"Scraping MaxPreps scores for {date_str}")
        games = []
        driver = None

        try:
            # MaxPreps loads games via JavaScript, so we need Selenium
            driver = self.get_selenium_driver()

            if driver is None:
                logger.error("Could not initialize Selenium driver - MaxPreps requires JavaScript")
                return games

            # Load the page and wait for JavaScript to render
            driver.get(url)

            # Wait for game elements to load (up to 10 seconds)
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            try:
                # Wait for contest boxes to appear
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "contest-box-item"))
                )
            except:
                logger.warning(f"No games found or timeout waiting for games on {date_str}")
                return games

            # Parse the rendered page with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Find all game containers using the actual MaxPreps structure
            game_containers = soup.find_all('div', class_='contest-box-item')

            logger.info(f"Found {len(game_containers)} game containers")

            for container in game_containers:
                try:
                    # Check if game has a score (completed games)
                    state = container.get('data-contest-state', '')
                    if state != 'boxscore':
                        continue  # Skip games that haven't been completed yet

                    # Find team list items
                    team_items = container.find('ul', class_='teams')
                    if not team_items:
                        continue

                    teams = team_items.find_all('li')
                    if len(teams) < 2:
                        continue

                    # Extract team names from <div class="name">
                    team1_name_elem = teams[0].find('div', class_='name')
                    team2_name_elem = teams[1].find('div', class_='name')

                    if not team1_name_elem or not team2_name_elem:
                        continue

                    team1_name = team1_name_elem.get_text(strip=True)
                    team2_name = team2_name_elem.get_text(strip=True)

                    # Find scores - they're in <div class="score">
                    team1_score_elem = teams[0].find('div', class_='score')
                    team2_score_elem = teams[1].find('div', class_='score')

                    if not team1_score_elem or not team2_score_elem:
                        continue

                    team1_score_text = team1_score_elem.get_text(strip=True)
                    team2_score_text = team2_score_elem.get_text(strip=True)

                    # Parse scores
                    try:
                        team1_score = int(team1_score_text)
                        team2_score = int(team2_score_text)
                    except ValueError:
                        logger.debug(f"Could not parse scores: {team1_score_text}, {team2_score_text}")
                        continue

                    # Normalize team names
                    team1_name = self.normalizer.find_canonical_name([team1_name]) or team1_name
                    team2_name = self.normalizer.find_canonical_name([team2_name]) or team2_name

                    game = {
                        'date': target_date.date(),
                        'team1_name': team1_name,
                        'team1_score': team1_score,
                        'team2_name': team2_name,
                        'team2_score': team2_score,
                        'source': 'MaxPreps'
                    }
                    games.append(game)
                    logger.debug(f"Found game: {team1_name} {team1_score} vs {team2_name} {team2_score}")

                except Exception as e:
                    logger.debug(f"Error parsing game container: {e}")
                    continue

            logger.info(f"Successfully scraped {len(games)} games from MaxPreps for {date_str}")

        except Exception as e:
            logger.error(f"Error scraping MaxPreps daily scores: {e}")
            import traceback
            logger.error(traceback.format_exc())

        finally:
            if driver:
                driver.quit()

        return games

    def scrape_recent_games(self, days_back=1):
        """
        Scrape recent game results from MaxPreps
        Uses the daily scores endpoint for each day
        """
        logger.info(f"Scraping MaxPreps for games from last {days_back} days")

        all_games = []

        for days_ago in range(days_back):
            target_date = datetime.now() - timedelta(days=days_ago+1)
            games = self.scrape_daily_scores(target_date)
            all_games.extend(games)

        logger.info(f"MaxPreps scraping complete: {len(all_games)} games found")
        return all_games


class TexasNewspaperScraper:
    """Scraper for major Texas newspaper sports sections"""

    NEWSPAPERS = {
        'Dallas Morning News': 'https://www.dallasnews.com/high-school-sports/basketball/',
        'Houston Chronicle': 'https://www.houstonchronicle.com/highschoolsports/',
        'Austin American-Statesman': 'https://www.statesman.com/sports/high-school/',
        'San Antonio Express-News': 'https://www.expressnews.com/sports/high_school/'
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def scrape_newspaper_scores(self, newspaper_name):
        """Scrape scores from a specific newspaper"""
        logger.info(f"Scraping {newspaper_name}")

        games = []

        try:
            url = self.NEWSPAPERS.get(newspaper_name)
            if not url:
                return games

            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # TODO: Implement newspaper-specific scraping logic
            # Each newspaper has different HTML structure
            # Would need to:
            # 1. Find score reporting elements
            # 2. Extract team names and scores
            # 3. Handle different date formats

            logger.warning(f"{newspaper_name} scraping not fully implemented")

        except Exception as e:
            logger.error(f"Error scraping {newspaper_name}: {e}")

        return games

    def scrape_all_newspapers(self):
        """Scrape all configured newspapers"""
        all_games = []

        for newspaper_name in self.NEWSPAPERS.keys():
            games = self.scrape_newspaper_scores(newspaper_name)
            all_games.extend(games)

        return all_games


class GASONRankingsScraper:
    """Scraper for GASO (Georgia Association of Scholarship Officials) rankings"""

    GASO_URL = "https://gasofastbreak.substack.com/p/gaso-2027-rankings-refresh-top-150"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.normalizer = SchoolNameNormalizer()

    def scrape_gaso_rankings(self):
        """
        Scrape GASO 2027 rankings from Substack
        Returns: List of ranked teams
        """
        logger.info("Scraping GASO rankings from Substack...")

        teams = []

        try:
            response = self.session.get(self.GASO_URL, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Substack posts are in article containers
                article = soup.find('article') or soup.find('div', class_='post')

                if article:
                    # Look for numbered lists or ranking structures
                    # Rankings are often in ordered lists or paragraphs with numbers
                    text_content = article.get_text()

                    # Parse rankings from text
                    # Pattern: "1. Team Name" or "1) Team Name" or "#1 Team Name"
                    ranking_patterns = [
                        r'(\d+)[.)]\s+([A-Za-z\s\-\']+)',  # 1. Team Name or 1) Team Name
                        r'#(\d+)\s+([A-Za-z\s\-\']+)',     # #1 Team Name
                        r'(\d+)\.\s+([A-Za-z\s\-\']+)\s+\(', # 1. Team Name (record)
                    ]

                    for pattern in ranking_patterns:
                        matches = re.findall(pattern, text_content)
                        if matches and len(matches) >= 10:  # Valid if we find at least 10 rankings
                            for rank_str, team_name in matches:
                                rank = int(rank_str)
                                team_name = team_name.strip()

                                # Normalize team name
                                team_name = self.normalizer.find_canonical_name([team_name]) or team_name

                                teams.append({
                                    'rank': rank,
                                    'team_name': team_name,
                                    'source': 'GASO'
                                })

                            logger.info(f"Found {len(teams)} teams from GASO rankings")
                            break

                if not teams:
                    logger.warning("Could not parse GASO rankings from page")

        except Exception as e:
            logger.error(f"Error scraping GASO rankings: {e}")

        return teams


class BoxScoreCollector:
    """Main collector that orchestrates all scrapers"""

    def __init__(self, app=None):
        self.app = app
        self.maxpreps_scraper = MaxPrepsBoxScoreScraper()
        self.newspaper_scraper = TexasNewspaperScraper()
        self.gaso_scraper = GASONRankingsScraper()
        self.normalizer = SchoolNameNormalizer()

    def collect_daily_box_scores(self, target_dates=None):
        """
        Collect box scores from all sources with deduplication

        Args:
            target_dates: List of datetime objects or date strings (MM/DD/YYYY) to scrape
                         If None, scrapes yesterday's games
        """
        logger.info("="*50)
        logger.info("Starting daily box score collection")
        logger.info("="*50)

        all_games = []

        # Convert date strings to datetime objects if needed
        dates_to_scrape = []
        if target_dates:
            for date_item in target_dates:
                if isinstance(date_item, str):
                    # Parse MM/DD/YYYY format
                    try:
                        dt = datetime.strptime(date_item, '%m/%d/%Y')
                        dates_to_scrape.append(dt)
                    except ValueError as e:
                        logger.error(f"Invalid date format '{date_item}': {e}")
                elif isinstance(date_item, datetime):
                    dates_to_scrape.append(date_item)

        # Scrape MaxPreps
        if dates_to_scrape:
            # Scrape specific dates
            logger.info(f"Scraping MaxPreps for {len(dates_to_scrape)} specific dates...")
            for target_date in dates_to_scrape:
                logger.info(f"Scraping MaxPreps for {target_date.strftime('%m/%d/%Y')}...")
                games = self.maxpreps_scraper.scrape_daily_scores(target_date)
                all_games.extend(games)
                logger.info(f"Found {len(games)} games for {target_date.strftime('%m/%d/%Y')}")
        else:
            # Default: scrape yesterday
            logger.info("Scraping MaxPreps daily scores...")
            maxpreps_games = self.maxpreps_scraper.scrape_recent_games(days_back=1)
            all_games.extend(maxpreps_games)

        logger.info(f"Total MaxPreps games: {len(all_games)}")

        # Scrape newspapers
        logger.info("Scraping Texas newspapers...")
        newspaper_games = self.newspaper_scraper.scrape_all_newspapers()
        all_games.extend(newspaper_games)
        logger.info(f"Found {len(newspaper_games)} games from newspapers")

        # Scrape GASO rankings (weekly, not daily - check day of week)
        today = datetime.now()
        if today.weekday() == 0:  # Monday
            logger.info("Scraping GASO rankings (weekly)...")
            gaso_teams = self.gaso_scraper.scrape_gaso_rankings()
            logger.info(f"Found {len(gaso_teams)} teams from GASO rankings")
            # GASO rankings are stored separately, not as games

        # Deduplicate games before saving
        logger.info(f"Deduplicating {len(all_games)} games...")
        all_games = self.deduplicate_games(all_games)
        logger.info(f"After deduplication: {len(all_games)} unique games")

        # Save to database
        if self.app and all_games:
            with self.app.app_context():
                saved_count = self.save_games_to_db(all_games)
                logger.info(f"Saved {saved_count} new games to database")

        logger.info(f"Total unique games collected: {len(all_games)}")
        logger.info("Daily box score collection complete")

        return all_games

    def deduplicate_games(self, games):
        """
        Deduplicate games by checking for duplicate team matchups
        Handles school name variations (Arlington vs Arl, etc.)
        """
        if not games:
            return []

        unique_games = []
        seen_matchups = set()

        for game in games:
            team1 = game.get('team1_name', '')
            team2 = game.get('team2_name', '')
            date = game.get('date')

            # Normalize team names
            norm_team1 = self.normalizer.normalize(team1)
            norm_team2 = self.normalizer.normalize(team2)

            # Create matchup key (alphabetically sorted to catch A vs B and B vs A)
            teams_sorted = tuple(sorted([norm_team1, norm_team2]))
            matchup_key = (date, teams_sorted)

            # Check for duplicates
            if matchup_key in seen_matchups:
                logger.debug(f"Duplicate found: {team1} vs {team2} on {date}")
                continue

            # Check if similar teams already exist
            is_duplicate = False
            for existing_key in seen_matchups:
                if existing_key[0] == date:  # Same date
                    existing_teams = existing_key[1]
                    # Check if teams are similar enough to be duplicates
                    if (self.normalizer.are_duplicates(teams_sorted[0], existing_teams[0]) and
                        self.normalizer.are_duplicates(teams_sorted[1], existing_teams[1])):
                        is_duplicate = True
                        logger.debug(f"Similar matchup found: {team1} vs {team2} ~ existing game")
                        break

            if not is_duplicate:
                seen_matchups.add(matchup_key)
                unique_games.append(game)

        return unique_games

    def save_games_to_db(self, games):
        """Save scraped games to database"""
        saved_count = 0

        for game in games:
            try:
                # Check if game already exists
                existing = BoxScore.query.filter_by(
                    game_date=game.get('date'),
                    team1_name=game.get('team1_name'),
                    team2_name=game.get('team2_name')
                ).first()

                if existing:
                    logger.debug(f"Game already exists: {game['team1_name']} vs {game['team2_name']}")
                    continue

                # Create new box score
                box_score = BoxScore(
                    game_date=game.get('date'),
                    classification=game.get('classification', 'AAAAAA'),
                    team1_name=game.get('team1_name'),
                    team1_score=game.get('team1_score'),
                    team1_fg=game.get('team1_fg'),
                    team1_fga=game.get('team1_fga'),
                    team1_3pt=game.get('team1_3pt'),
                    team1_3pta=game.get('team1_3pta'),
                    team1_ft=game.get('team1_ft'),
                    team1_fta=game.get('team1_fta'),
                    team1_reb=game.get('team1_reb'),
                    team1_ast=game.get('team1_ast'),
                    team1_stl=game.get('team1_stl'),
                    team1_blk=game.get('team1_blk'),
                    team1_to=game.get('team1_to'),
                    team2_name=game.get('team2_name'),
                    team2_score=game.get('team2_score'),
                    team2_fg=game.get('team2_fg'),
                    team2_fga=game.get('team2_fga'),
                    team2_3pt=game.get('team2_3pt'),
                    team2_3pta=game.get('team2_3pta'),
                    team2_ft=game.get('team2_ft'),
                    team2_fta=game.get('team2_fta'),
                    team2_reb=game.get('team2_reb'),
                    team2_ast=game.get('team2_ast'),
                    team2_stl=game.get('team2_stl'),
                    team2_blk=game.get('team2_blk'),
                    team2_to=game.get('team2_to'),
                    submitted_by='Auto-scraped'
                )

                db.session.add(box_score)
                saved_count += 1

            except Exception as e:
                logger.error(f"Error saving game: {e}")
                continue

        if saved_count > 0:
            db.session.commit()

        return saved_count


if __name__ == '__main__':
    # Test the scrapers
    print("Testing Box Score Scrapers")
    print("="*50)

    collector = BoxScoreCollector()
    games = collector.collect_daily_box_scores()

    print(f"\nCollected {len(games)} games")
