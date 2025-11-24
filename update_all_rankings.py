"""
Update rankings with latest data from all sources
Combines: TABC, MaxPreps, GASO, and calculated ratings
"""

from app import app
from scheduler import update_rankings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("="*70)
    logger.info("UPDATING RANKINGS WITH LATEST DATA FROM ALL SOURCES")
    logger.info("="*70)
    logger.info("")
    logger.info("Sources:")
    logger.info("  - TABC (Texas Association of Basketball Coaches)")
    logger.info("  - MaxPreps (Daily updated rankings)")
    logger.info("  - GASO (Great American Shoot Out pre-season)")
    logger.info("  - Calculated efficiency ratings from game data")
    logger.info("")

    # Run within app context
    with app.app_context():
        update_rankings()

    logger.info("")
    logger.info("="*70)
    logger.info("RANKINGS UPDATE COMPLETE")
    logger.info("="*70)
