STATUS_NEW = 0 
STATUS_MORE_INFORMATION = 1
STATUS_IN_PROGRESS = 2
STATUS_TESTING = 3
STATUS_PULL_REQUEST = 4
STATUS_COMPLETE = 5

MILESTONE_STATUS_IDS = [STATUS_NEW, STATUS_IN_PROGRESS, STATUS_COMPLETE]
STATUS_IDS = [0, 1, 2, 3, 4, 5]
TICKET_STATUS_IDS = [STATUS_NEW, STATUS_MORE_INFORMATION, STATUS_IN_PROGRESS, STATUS_TESTING, STATUS_PULL_REQUEST, STATUS_COMPLETE]

STATUS_LIST = {
    STATUS_NEW: 'New',
    STATUS_MORE_INFORMATION: 'Requires more information',
    STATUS_IN_PROGRESS: 'in progress',
    STATUS_TESTING: 'Testing',
    STATUS_PULL_REQUEST: 'Pull request',
    STATUS_COMPLETE: 'Complete'}

PAGINATION_ROWS = 50

