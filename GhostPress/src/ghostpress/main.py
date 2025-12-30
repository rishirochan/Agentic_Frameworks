#!/usr/bin/env python
import warnings
from datetime import datetime

from ghostpress.crew import Ghostpress

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """Run the Syndicate crew to create content and send email campaign."""
    inputs = {
        'topic': 'LiDar Technology in Autonomous Vehicles',
        'current_year': str(datetime.now().year)
    }

    result = Ghostpress().crew().kickoff(inputs=inputs)
    return result


if __name__ == "__main__":
    run()
