from rest_framework import status, viewsets
from rest_framework.response import Response
from django.db.models import Q
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware

class SearchableListModelMixin(viewsets.ModelViewSet):
    time_range_fields = []

    def list(self, request, *args, **kwargs):
        query_params = request.query_params
        serializer_fields = set(self.get_serializer().fields.keys())
        query = Q()

        # 普通字段模糊查询（排除时间范围字段）
        for field, value in query_params.items():
            if field in serializer_fields and field not in self.time_range_fields and value:
                query.add(Q(**{f'{field}__icontains': value}), Q.AND)

        # 时间范围查询
        for time_field in self.time_range_fields:
            time_values = query_params.getlist(f'{time_field}[]')
            if time_values and len(time_values) == 2:
                start_date = parse_datetime(time_values[0])
                end_date = parse_datetime(time_values[1])
                if start_date and end_date:
                    start_date = make_aware(start_date)
                    end_date = make_aware(end_date)
                    query.add(Q(**{f'{time_field}__range': (start_date, end_date)}), Q.AND)

        # 查询和排序
        queryset = self.get_queryset().filter(query).order_by('id')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
