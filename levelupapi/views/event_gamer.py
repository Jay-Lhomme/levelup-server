"""View module for handling requests about games"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from levelupapi.models import EventGamer, Event, Gamer


class EventGamerView(ViewSet):
    """Level up game types view"""

    def retrieve(self, request, pk):
        """Handle GET requests for single game type

        Returns:
            Response -- JSON serialized game type
        """
        try:
            event_gamer = EventGamer.objects.get(pk=pk)
            serializer = EventGamerSerializer(event_gamer)
            return Response(serializer.data)
        except EventGamer.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        """Handle GET requests to get all game types

        Returns:
            Response -- JSON serialized list of game types
        """
        event_gamers = EventGamer.objects.all()

        serializer = EventGamerSerializer(event_gamers, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized EventGamer instance
        """
        event = Event.objects.get(pk=request.data["eventId"])
        gamer = Gamer.objects.get(pk=request.data["gamerId"])

        event_gamer = EventGamer.objects.create(
            event=event,
            gamer=gamer,
        )
        serializer = EventGamerSerializer(event_gamer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk):
        """Handle PUT requests for an eventgamer

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            event_gamer = EventGamer.objects.get(pk=pk)
            event = Event.objects.get(pk=request.data["eventId"])
            event_gamer.event = event
            gamer = Gamer.objects.get(pk=request.data["gamerId"])
            event_gamer.gamer = gamer
            event.save()
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except EventGamer.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk):
        """Handle DELETE requests for a game type

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            event_gamer = EventGamer.objects.get(pk=pk)
            event_gamer.delete()
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except EventGamer.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)


class EventGamerSerializer(serializers.ModelSerializer):
    """JSON serializer for game types"""
    class Meta:
        model = EventGamer
        fields = ('id', 'event_id', 'gamer_id')
