from django.contrib.auth.models import User
from djblets.testing.decorators import add_fixtures
from djblets.webapi.errors import PERMISSION_DENIED

from reviewboard.webapi.tests.base import BaseWebAPITestCase
from reviewboard.webapi.tests.mimetypes import (
    screenshot_comment_item_mimetype,
    screenshot_comment_list_mimetype)
from reviewboard.webapi.tests.urls import (
    get_review_screenshot_comment_item_url,
    get_review_screenshot_comment_list_url)


class BaseTestCase(BaseWebAPITestCase):
    fixtures = ['test_users']

    def _create_screenshot_review_with_issue(self, publish=False,
                                             comment_text=None):
        """Sets up a review for a screenshot that includes an open issue.

        If `publish` is True, the review is published. The review request is
        always published.

        Returns the response from posting the comment, the review object, and
        the review request object.
        """
        if not comment_text:
            comment_text = 'Test screenshot comment with an opened issue'

        review_request = self.create_review_request(publish=True,
                                                    submitter=self.user)
        screenshot = self.create_screenshot(review_request)
        review = self.create_review(review_request, user=self.user,
                                    publish=publish)
        comment = self.create_screenshot_comment(review, screenshot,
                                                 comment_text,
                                                 issue_opened=True)

        return comment, review, review_request


class ResourceListTests(BaseTestCase):
    """Testing the ReviewScreenshotCommentResource list APIs."""

    #
    # HTTP POST tests
    #

    def test_post(self):
        """Testing the
        POST review-requests/<id>/reviews/<id>/screenshot-comments/ API
        """
        comment_text = "This is a test comment."
        x, y, w, h = (2, 2, 10, 10)

        review_request = self.create_review_request(publish=True)
        screenshot = self.create_screenshot(review_request)
        review = self.create_review(review_request, user=self.user)

        rsp = self._postNewScreenshotComment(review_request, review.id,
                                             screenshot, comment_text,
                                             x, y, w, h)

        self.assertEqual(rsp['screenshot_comment']['text'], comment_text)
        self.assertEqual(rsp['screenshot_comment']['x'], x)
        self.assertEqual(rsp['screenshot_comment']['y'], y)
        self.assertEqual(rsp['screenshot_comment']['w'], w)
        self.assertEqual(rsp['screenshot_comment']['h'], h)

    @add_fixtures(['test_site'])
    def test_post_with_site(self):
        """Testing the
        POST review-requests/<id>/reviews/<id>/screenshot-comments/ API
        with a local site
        """
        comment_text = 'This is a test comment.'
        x, y, w, h = (2, 2, 10, 10)

        user = self._login_user(local_site=True)

        review_request = self.create_review_request(with_local_site=True,
                                                    publish=True)
        screenshot = self.create_screenshot(review_request)
        review = self.create_review(review_request, user=user)

        rsp = self._postNewScreenshotComment(review_request, review.id,
                                             screenshot, comment_text,
                                             x, y, w, h)

        self.assertEqual(rsp['screenshot_comment']['text'], comment_text)
        self.assertEqual(rsp['screenshot_comment']['x'], x)
        self.assertEqual(rsp['screenshot_comment']['y'], y)
        self.assertEqual(rsp['screenshot_comment']['w'], w)
        self.assertEqual(rsp['screenshot_comment']['h'], h)

    def test_post_with_issue(self):
        """Testing the
        POST review-requests/<id>/reviews/<id>/screenshot-comments/ API
        with an issue
        """
        comment_text = "Test screenshot comment with an opened issue"
        comment, review, review_request = \
            self._create_screenshot_review_with_issue(
                publish=False, comment_text=comment_text)

        rsp = self.apiGet(
            get_review_screenshot_comment_list_url(review),
            expected_mimetype=screenshot_comment_list_mimetype)
        self.assertEqual(rsp['stat'], 'ok')
        self.assertTrue('screenshot_comments' in rsp)
        self.assertEqual(len(rsp['screenshot_comments']), 1)
        self.assertEqual(rsp['screenshot_comments'][0]['text'], comment_text)
        self.assertTrue(rsp['screenshot_comments'][0]['issue_opened'])

    @add_fixtures(['test_site'])
    def test_post_with_site_no_access(self):
        """Testing the
        POST review-requests/<id>/reviews/<id>/screenshot-comments/ API
        with a local site and Permission Denied error
        """
        x, y, w, h = (2, 2, 10, 10)

        user = self._login_user(local_site=True)

        review_request = self.create_review_request(with_local_site=True,
                                                    publish=True)
        screenshot = self.create_screenshot(review_request)
        review = self.create_review(review_request, user=user)

        self._login_user()

        rsp = self.apiPost(
            get_review_screenshot_comment_list_url(review,
                                                   self.local_site_name),
            {'screenshot_id': screenshot.id},
            expected_status=403)
        self.assertEqual(rsp['stat'], 'fail')
        self.assertEqual(rsp['err']['code'], PERMISSION_DENIED.code)


class ResourceItemTests(BaseTestCase):
    """Testing the ReviewScreenshotCommentResource item APIs."""
    fixtures = ['test_users']

    #
    # HTTP DELETE tests
    #

    def test_delete(self):
        """Testing the
        DELETE review-requests/<id>/reviews/<id>/screenshot-comments/<id>/ API
        """
        comment_text = "This is a test comment."
        x, y, w, h = (2, 2, 10, 10)

        review_request = self.create_review_request(publish=True)
        screenshot = self.create_screenshot(review_request)
        review = self.create_review(review_request, user=self.user)
        comment = self.create_screenshot_comment(review, screenshot,
                                                 comment_text, x, y, w, h)

        self.apiDelete(
            get_review_screenshot_comment_item_url(review, comment.pk))

        rsp = self.apiGet(
            get_review_screenshot_comment_list_url(review),
            expected_mimetype=screenshot_comment_list_mimetype)
        self.assertEqual(rsp['stat'], 'ok')
        self.assertTrue('screenshot_comments' in rsp)
        self.assertEqual(len(rsp['screenshot_comments']), 0)

    @add_fixtures(['test_site'])
    def test_delete_with_local_site(self):
        """Testing the
        DELETE review-requests/<id>/reviews/<id>/screenshot-comments/<id> API
        with a local site
        """
        comment_text = 'This is a test comment.'
        x, y, w, h = (2, 2, 10, 10)

        user = self._login_user(local_site=True)

        review_request = self.create_review_request(with_local_site=True,
                                                    publish=True)
        screenshot = self.create_screenshot(review_request)
        review = self.create_review(review_request, user=user)
        comment = self.create_screenshot_comment(review, screenshot,
                                                 comment_text, x, y, w, h)

        self.apiDelete(
            get_review_screenshot_comment_item_url(review, comment.pk,
                                                   self.local_site_name))

        rsp = self.apiGet(
            get_review_screenshot_comment_list_url(review,
                                                   self.local_site_name),
            expected_mimetype=screenshot_comment_list_mimetype)
        self.assertEqual(rsp['stat'], 'ok')
        self.assertTrue('screenshot_comments' in rsp)
        self.assertEqual(len(rsp['screenshot_comments']), 0)

    @add_fixtures(['test_site'])
    def test_delete_with_local_site_no_access(self):
        """Testing the
        DELETE review-requests/<id>/reviews/<id>/screenshot-comments/<id> API
        with a local site and Permission Denied error
        """
        comment_text = 'This is a test comment.'
        x, y, w, h = (2, 2, 10, 10)

        user = self._login_user(local_site=True)

        review_request = self.create_review_request(with_local_site=True,
                                                    publish=True)
        screenshot = self.create_screenshot(review_request)
        review = self.create_review(review_request, user=user)
        comment = self.create_screenshot_comment(review, screenshot,
                                                 comment_text, x, y, w, h)

        self.apiDelete(
            get_review_screenshot_comment_item_url(review, comment.pk,
                                                   self.local_site_name))

        self._login_user()

        rsp = self.apiDelete(
            get_review_screenshot_comment_item_url(review, comment.pk,
                                                   self.local_site_name),
            expected_status=403)
        self.assertEqual(rsp['stat'], 'fail')
        self.assertEqual(rsp['err']['code'], PERMISSION_DENIED.code)

    def test_delete_with_does_not_exist_error(self):
        """Testing the
        DELETE review-requests/<id>/reviews/<id>/screenshot-comments/<id>/ API
        with Does Not Exist error
        """
        x, y, w, h = (2, 2, 10, 10)

        review_request = self.create_review_request(publish=True)
        self.create_screenshot(review_request)
        review = self.create_review(review_request, user=self.user)

        self.apiDelete(get_review_screenshot_comment_item_url(review, 123),
                       expected_status=404)

    #
    # HTTP PUT tests
    #

    def test_put_with_issue(self):
        """Testing the
        PUT review-requests/<id>/reviews/<id>/screenshot-comments/<id>/ API
        with an issue, removing issue_opened
        """
        comment, review, review_request = \
            self._create_screenshot_review_with_issue()

        rsp = self.apiPut(
            get_review_screenshot_comment_item_url(review, comment.pk),
            {'issue_opened': False},
            expected_mimetype=screenshot_comment_item_mimetype)
        self.assertEqual(rsp['stat'], 'ok')
        self.assertFalse(rsp['screenshot_comment']['issue_opened'])

    def test_put_issue_status_before_publish(self):
        """Testing the
        PUT review-requests/<id>/reviews/<id>/screenshot-comments/<id> API
        with an issue, before review is published
        """
        comment, review, review_request = \
            self._create_screenshot_review_with_issue()

        # The issue_status should not be able to be changed while the review is
        # unpublished.
        rsp = self.apiPut(
            get_review_screenshot_comment_item_url(review, comment.pk),
            {'issue_status': 'resolved'},
            expected_mimetype=screenshot_comment_item_mimetype)

        self.assertEqual(rsp['stat'], 'ok')

        # The issue_status should still be "open"
        self.assertEqual(rsp['screenshot_comment']['issue_status'], 'open')

    def test_put_issue_status_after_publish(self):
        """Testing the
        PUT review-requests/<id>/reviews/<id>/screenshot-comments/<id>/ API
        with an issue, after review is published
        """
        comment, review, review_request = \
            self._create_screenshot_review_with_issue(publish=True)

        rsp = self.apiPut(
            get_review_screenshot_comment_item_url(review, comment.pk),
            {'issue_status': 'resolved'},
            expected_mimetype=screenshot_comment_item_mimetype)
        self.assertEqual(rsp['stat'], 'ok')
        self.assertEqual(rsp['screenshot_comment']['issue_status'], 'resolved')

    def test_put_issue_status_by_issue_creator(self):
        """Testing the
        PUT review-requests/<id>/reviews/<id>/screenshot-comments/<id>/ API
        permissions for issue creator
        """
        comment, review, review_request = \
            self._create_screenshot_review_with_issue(publish=True)

        # Change the owner of the review request so that it's not owned by
        # self.user
        review_request.submitter = User.objects.get(username='doc')
        review_request.save()

        # The review/comment (and therefore issue) is still owned by self.user,
        # so we should be able to change the issue status.
        rsp = self.apiPut(
            get_review_screenshot_comment_item_url(review, comment.pk),
            {'issue_status': 'dropped'},
            expected_mimetype=screenshot_comment_item_mimetype)
        self.assertEqual(rsp['stat'], 'ok')
        self.assertEqual(rsp['screenshot_comment']['issue_status'], 'dropped')

    def test_put_issue_status_by_uninvolved_user(self):
        """Testing the
        PUT review-requests/<id>/reviews/<id>/screenshot-comments/<id>/ API
        permissions for an uninvolved user
        """
        comment, review, review_request = \
            self._create_screenshot_review_with_issue(publish=True)

        # Change the owner of the review request and review so that they're not
        # owned by self.user.
        new_owner = User.objects.get(username='doc')
        review_request.submitter = new_owner
        review_request.save()
        review.user = new_owner
        review.save()

        rsp = self.apiPut(
            get_review_screenshot_comment_item_url(review, comment.pk),
            {'issue_status': 'dropped'},
            expected_status=403)
        self.assertEqual(rsp['stat'], 'fail')
        self.assertEqual(rsp['err']['code'], PERMISSION_DENIED.code)

    def test_put_deleted_screenshot_comment_issue_status(self):
        """Testing the
        PUT review-requests/<id>/reviews/<id>/screenshot-comments/<id>
        API with an issue and a deleted screenshot
        """
        comment_text = "Test screenshot comment with an opened issue"
        x, y, w, h = (2, 2, 10, 10)

        review_request = self.create_review_request(publish=True,
                                                    submitter=self.user)
        screenshot = self.create_screenshot(review_request)
        review = self.create_review(review_request, user=self.user)
        comment = self.create_screenshot_comment(review, screenshot,
                                                 comment_text, x, y, w, h,
                                                 issue_opened=True)

        # First, let's ensure that the user that has created the comment
        # cannot alter the issue_status while the review is unpublished.
        rsp = self.apiPut(
            get_review_screenshot_comment_item_url(review, comment.pk),
            {'issue_status': 'resolved'},
            expected_mimetype=screenshot_comment_item_mimetype)

        self.assertEqual(rsp['stat'], 'ok')

        # The issue_status should still be "open"
        self.assertEqual(rsp['screenshot_comment']['issue_status'], 'open')

        # Next, let's publish the review, and try altering the issue_status.
        # This should be allowed, since the review request was made by the
        # current user.
        review.public = True
        review.save()

        rsp = self.apiPut(
            rsp['screenshot_comment']['links']['self']['href'],
            {'issue_status': 'resolved'},
            expected_mimetype=screenshot_comment_item_mimetype)
        self.assertEqual(rsp['stat'], 'ok')
        self.assertEqual(rsp['screenshot_comment']['issue_status'], 'resolved')

        # Delete the screenshot.
        self._delete_screenshot(review_request, screenshot)
        review_request.publish(review_request.submitter)

        # Try altering the issue_status. This should be allowed.
        rsp = self.apiPut(
            rsp['screenshot_comment']['links']['self']['href'],
            {'issue_status': 'open'},
            expected_mimetype=screenshot_comment_item_mimetype)
        self.assertEqual(rsp['stat'], 'ok')
        self.assertEqual(rsp['screenshot_comment']['issue_status'], 'open')
