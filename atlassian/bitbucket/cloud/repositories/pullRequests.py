# coding=utf-8

from ..base import BitbucketCloudBase
from ..common.users import User


class PullRequests(BitbucketCloudBase):
    """
    Bitbucket Cloud pull requests

    API docs: https://developer.atlassian.com/bitbucket/api/2/reference/resource/repositories/%7Bworkspace%7D/%7Brepo_slug%7D/pullrequests#get
    """

    def __init__(self, url, *args, **kwargs):
        super(PullRequests, self).__init__(url, *args, **kwargs)

    def __get_object(self, data):
        if "errors" in data:
            return
        return PullRequest(self.url_joiner(self.url, data["id"]), data, **self._new_session_args)

    def each(self, q=None, sort=None):
        """
        Returns the list of pull requests in this repository.

        :param q: string: Query string to narrow down the response.
                          See https://developer.atlassian.com/bitbucket/api/2/reference/meta/filtering for details.
        :param sort: string: Name of a response property to sort results.
                             See https://developer.atlassian.com/bitbucket/api/2/reference/meta/filtering for details.

        :return: A generator for the PullRequest objects
        """
        params = {}
        if sort is not None:
            params["sort"] = sort
        if q is not None:
            params["q"] = q
        for pr in self._get_paged(None, trailing=True, params=params):
            yield self.__get_object(pr)

        return

    def get(self, id):
        """
        Returns the pull requests with the requested id in this repository.

        :param id: int: The requested pull request id

        :return: The requested PullRequest object
        """
        return self.__get_object(super(PullRequests, self).get(id))

    # def add(self):
    #     TODO add a new pull request
    #     TODO https://developer.atlassian.com/bitbucket/api/2/reference/resource/repositories/%7Bworkspace%7D/%7Brepo_slug%7D/pullrequests#post
    #     return PullRequest object


class PullRequest(BitbucketCloudBase):
    """
    Bitbucket Cloud pull request endpoint

    See https://developer.atlassian.com/bitbucket/api/2/reference/resource/repositories/%7Bworkspace%7D/%7Brepo_slug%7D/pullrequests/%7Bpull_request_id%7D
    """

    MERGE_COMMIT = "merge_commit"
    MERGE_SQUASH = "squash"
    MERGE_FF = "fast_forward"
    MERGE_STRATEGIES = [
        MERGE_COMMIT,
        MERGE_SQUASH,
        MERGE_FF,
    ]
    STATE_OPEN = "OPEN"
    STATE_DECLINED = "DECLINED"
    STATE_MERGED = "MERGED"
    STATE_SUPERSEDED = "SUPERSEDED"

    def __init__(self, url, data, *args, **kwargs):
        super(PullRequest, self).__init__(url, *args, data=data, expected_type="pullrequest", **kwargs)

    def _check_if_open(self):
        if not self.is_open:
            raise Exception("Pull Request isn't open")
        return

    @property
    def id(self):
        """ unique pull request id """
        return self.get_data("id")

    @property
    def title(self):
        """ pull request title """
        return self.get_data("title")

    @property
    def description(self):
        """ pull request description """
        return self.get_data("description")

    @property
    def is_declined(self):
        """ True if the pull request was declined """
        return self.get_data("state") == self.STATE_DECLINED

    @property
    def is_merged(self):
        """ True if the pull request was merged """
        return self.get_data("state") == self.STATE_MERGED

    @property
    def is_open(self):
        """ True if the pull request is open """
        return self.get_data("state") == self.STATE_OPEN

    @property
    def is_superseded(self):
        """ True if the pull request was superseded """
        return self.get_data("state") == self.STATE_SUPERSEDED

    @property
    def created_on(self):
        """ time of creation """
        return self.get_time("created_on")

    @property
    def updated_on(self):
        """ time of last update """
        return self.get_time("updated_on")

    @property
    def default_merge_strategy(self):
        """ default merge strategy """
        # TODO this wont work....
        return self.get_data("destination")["branch"]["default_merge_strategy"]

    @property
    def close_source_branch(self):
        """ close source branch flag """
        return self.get_data("close_source_branch")

    @property
    def source_branch(self):
        """ source branch """
        return self.get_data("source")["branch"]["name"]

    @property
    def destination_branch(self):
        """ destination branch """
        return self.get_data("destination")["branch"]["name"]

    @property
    def comment_count(self):
        """ number of comments """
        return self.get_data("comment_count")

    @property
    def task_count(self):
        """ number of tasks """
        return self.get_data("task_count")

    @property
    def declined_reason(self):
        """ reason for declining """
        return self.get_data("reason")

    @property
    def author(self):
        """ User object of the author """
        return User(None, self.get_data("author"))

    def participants(self):
        """ Returns a generator object of participants """
        for participant in self.get_data("participants"):
            yield Participant(participant, **self._new_session_args)

        return

    def reviewers(self):
        """ Returns a generator object of reviewers """
        for reviewer in self.get_data("reviewers"):
            yield User(None, reviewer, **self._new_session_args)

        return

    def comment(self, raw_message):
        """
        Commenting the pull request in raw format

        API docs: https://developer.atlassian.com/bitbucket/api/2/reference/resource/repositories/%7Bworkspace%7D/%7Brepo_slug%7D/pullrequests/%7Bpull_request_id%7D/comments#post
        """
        if not raw_message:
            raise ValueError("No message set")

        data = {
            "content": {
                "raw": raw_message,
            }
        }

        return self.post("comments", data)

    def approve(self):
        """
        Approve a pull request if open

        API docs: https://developer.atlassian.com/bitbucket/api/2/reference/resource/repositories/%7Bworkspace%7D/%7Brepo_slug%7D/pullrequests/%7Bpull_request_id%7D/approve#post
        """
        self._check_if_open()
        data = {"approved": True}
        return self.post("approve", data)

    def unapprove(self):
        """
        Unapprove a pull request if open

        API docs: https://developer.atlassian.com/bitbucket/api/2/reference/resource/repositories/%7Bworkspace%7D/%7Brepo_slug%7D/pullrequests/%7Bpull_request_id%7D/approve#delete
        """
        self._check_if_open()
        return self.delete("approve")

    def request_changes(self):
        """
        Request changes for the pull request if open

        API docs: https://developer.atlassian.com/bitbucket/api/2/reference/resource/repositories/%7Bworkspace%7D/%7Brepo_slug%7D/pullrequests/%7Bpull_request_id%7D/request-changes#post
        """
        self._check_if_open()
        data = {"request-changes": True}
        return self.post("request-changes", data)

    def unrequest_changes(self):
        """
        Request changes for the pull request if open

        API docs: https://developer.atlassian.com/bitbucket/api/2/reference/resource/repositories/%7Bworkspace%7D/%7Brepo_slug%7D/pullrequests/%7Bpull_request_id%7D/request-changes#delete
        """
        self._check_if_open()
        return self.delete("request-changes")

    def decline(self):
        """
        Decline a pull request

        API docs: https://developer.atlassian.com/bitbucket/api/2/reference/resource/repositories/%7Bworkspace%7D/%7Brepo_slug%7D/pullrequests/%7Bpull_request_id%7D/decline
        """
        self._check_if_open()
        return self.post("decline")

    def merge(self, merge_strategy=None, close_source_branch=None):
        """
        Merges the pull request if it's open
        :param merge_strategy: string:  Merge strategy (one of PullRequest.MERGE_COMMIT, PullRequest.MERGE_SQUASH, PullRequest.MERGE_FF), if None default merge strategy will be used
        :param close_source_branch: boolean: Close the source branch after merge, default PR option

        API docs: https://developer.atlassian.com/bitbucket/api/2/reference/resource/repositories/%7Bworkspace%7D/%7Brepo_slug%7D/pullrequests/%7Bpull_request_id%7D/merge
        """
        self._check_if_open()

        if merge_strategy is not None and merge_strategy not in self.MERGE_STRATEGIES:
            raise ValueError("merge_stragegy must be {}".format(self.MERGE_STRATEGIES))

        data = {
            "close_source_branch": close_source_branch or self.close_source_branch,
            "merge_strategy": merge_strategy,
        }

        return self.post("merge", data)


class Participant(BitbucketCloudBase):
    ROLE_REVIEWER = "REVIEWER"
    ROLE_PARTICIPANT = "PARTICIPANT"
    CHANGES_REQUESTED = "changes_requested"

    def __init__(self, data, *args, **kwargs):
        super(Participant, self).__init__(None, None, *args, data=data, expected_type="participant", **kwargs)

    @property
    def user(self):
        """ User object with user information of the participant """
        return User(None, self.get_data("user"), **self._new_session_args)

    @property
    def is_participant(self):
        """ True if the user is a pull request participant """
        return self.get_data("role") == self.ROLE_PARTICIPANT

    @property
    def is_reviewer(self):
        """ True if the user is a pull request reviewer """
        return self.get_data("role") == self.ROLE_REVIEWER

    @property
    def has_changes_requested(self):
        """ True if user requested changes """
        return str(self.get_data("state")) == self.CHANGES_REQUESTED

    @property
    def has_approved(self):
        """ True if user approved the pull request """
        return self.get_data("approved")

    @property
    def participated_on(self):
        """ time of last participation """
        return self.get_time("participated_on")
