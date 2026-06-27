from rest_framework import serializers

from ...models import Province,City,Neighborhood

class NeighborhoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Neighborhood
        fields = ('id','name','slug')

class CityListSerializer(serializers.ModelSerializer):
    neighborhoods = NeighborhoodSerializer(many=True, read_only=True)
    class Meta:
        model = City
        fields = ('id','name','slug','neighborhoods')

class CityDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id','name','slug')

class ProvinceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ('id','name','slug')


class ProvinceDetailSerializer(serializers.ModelSerializer):
    cities = CityListSerializer(many=True, read_only=True)
    class Meta:
        model = Province
        fields = ('id','name','slug','cities')

