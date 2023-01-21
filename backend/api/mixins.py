from rest_framework import mixins, viewsets


class GetViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """ViewSet с методом GET """
    pass
