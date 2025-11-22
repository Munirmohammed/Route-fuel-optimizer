from rest_framework import serializers


class RouteOptimizerRequestSerializer(serializers.Serializer):
    start_location = serializers.CharField(max_length=255)
    end_location = serializers.CharField(max_length=255)


class RouteOptimizerResponseSerializer(serializers.Serializer):
    route = serializers.DictField()
    fuel_stops = serializers.ListField()
    summary = serializers.DictField()
    map_html = serializers.CharField()
    performance = serializers.DictField()
