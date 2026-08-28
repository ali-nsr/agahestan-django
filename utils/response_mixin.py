# mixins/response_mixin.py
from rest_framework.response import Response
from rest_framework import status


class ResponseMixin:
    def success_response(self, data=None, message="Success", status_code=status.HTTP_200_OK):
        return Response({
            'success': True,
            'message': message,
            'data': data,
            'status_code': status_code
        }, status=status_code)

    def error_response(self, message="Error", status_code=status.HTTP_400_BAD_REQUEST, data=None):
        return Response({
            'success': False,
            'message': message,
            'data': data or {},
            'status_code': status_code
        }, status=status_code)

    def paginated_response(self, data, paginator, message="Success"):
        return Response({
            'success': True,
            'message': message,
            'data': {
                'results': data,
                'count': paginator.page.paginator.count,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
                'total_pages': paginator.page.paginator.num_pages
            },
            'status_code': status.HTTP_200_OK
        }, status=status.HTTP_200_OK)