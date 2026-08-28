# utils/exceptions.py
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        # اگر خطای سریالایزر باشه
        if hasattr(exc, 'detail') and isinstance(exc.detail, dict):
            formatted_errors = {}
            for field, errors in exc.detail.items():
                if isinstance(errors, list):
                    formatted_errors[field] = [str(err) for err in errors]
                else:
                    formatted_errors[field] = [str(errors)]

            # استخراج اولین پیام خطا
            first_error = None
            for field, errors_list in formatted_errors.items():
                if errors_list:
                    first_error = f"{field}: {errors_list[0]}"
                    break

            return Response({
                'success': False,
                'message': first_error or "Validation failed",
                'errors': formatted_errors,
                'status_code': response.status_code
            }, status=response.status_code)

        # سایر خطاها
        return Response({
            'success': False,
            'message': str(exc.detail) if hasattr(exc, 'detail') else str(exc),
            'errors': response.data,
            'status_code': response.status_code
        }, status=response.status_code)

    return Response({
        'success': False,
        'message': 'Internal server error',
        'status_code': 500
    }, status=500)
