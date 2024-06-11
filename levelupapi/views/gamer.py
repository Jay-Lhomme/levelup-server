"""View module for handling requests about games"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from levelupapi.models import Gamer


class GamerView(ViewSet):
    """Level up game types view"""

    def retrieve(self, request, pk):
        """Handle GET requests for single game type

        Returns:
            Response -- JSON serialized game type
        """
        try:
            gamer = Gamer.objects.get(pk=pk)
            serializer = GamerSerializer(gamer)
            return Response(serializer.data)
        except Gamer.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        """Handle GET requests to get all game types

        Returns:
            Response -- JSON serialized list of game types
        """
        gamers = Gamer.objects.all()
        serializer = GamerSerializer(gamers, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized gamer instance
        """
        gamer = Gamer.objects.create(
            bio=request.data["bio"],
            uid=request.data["uid"]
        )
        serializer = GamerSerializer(gamer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk):
        """Handle PUT requests for a game type

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            gamer = Gamer.objects.get(pk=pk)
            gamer.bio = request.data["bio"]
            gamer.uid = request.data["uid"]
            gamer.save()
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except Gamer.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk):
        """Handle DELETE requests for a game type

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            gamer = Gamer.objects.get(pk=pk)
            gamer.delete()
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except Gamer.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)


class GamerSerializer(serializers.ModelSerializer):
    """JSON serializer for game types"""
    class Meta:
        model = Gamer
        fields = ('id', 'bio', 'uid')
