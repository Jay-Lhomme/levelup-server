from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.decorators import action
from levelupapi.models import Event, Game, Gamer, EventGamer


class EventView(ViewSet):
    """Level up events view"""

    def retrieve(self, request, pk):
        """Handle GET requests for single event

        Returns:
            Response -- JSON serialized event
        """
        try:
            event = Event.objects.get(pk=pk)
            serializer = EventSerializer(event)
            return Response(serializer.data)
        except Event.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        """Handle GET requests to get all events

        Returns:
            Response -- JSON serialized list of events
        """

        events = Event.objects.all()

        game = request.query_params.get('game', None)
        if game is not None:
            events = events.filter(game_id=game)

        uid = request.META['HTTP_AUTHORIZATION']
        if not uid:
            return Response({'message': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            gamer = Gamer.objects.get(uid=uid)
        except Gamer.DoesNotExist:
            return Response({'message': 'Gamer not found'}, status=status.HTTP_404_NOT_FOUND)

        # for event in events:
        #     # Check to see if there is a row in the Event Games table that has the passed in gamer and event
        #     event.joined = len(EventGamer.objects.filter(
        #         gamer=gamer, event=event)) > 0

        for event in events:
            # Check if the gamer is attending the event
            event.joined = EventGamer.objects.filter(
                gamer=gamer, event=event).exists()

        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def signup(self, request, pk=None):
        # Implementation for signing up for an event
        pass

    @action(detail=True, methods=['delete'])
    def leave(self, request, pk=None):
        # Implementation for leaving an event
        pass

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized event instance
        """
        try:
            game = Game.objects.get(pk=request.data["gameId"])
            organizer = Gamer.objects.get(pk=request.data["organizerId"])

            event = Event.objects.create(
                description=request.data["description"],
                date=request.data["date"],
                time=request.data["time"],
                game=game,
                organizer=organizer,
            )
            serializer = EventSerializer(event)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Game.DoesNotExist:
            return Response({'message': 'Game not found'}, status=status.HTTP_404_NOT_FOUND)
        except Gamer.DoesNotExist:
            return Response({'message': 'Organizer not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response({'message': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk):
        """Handle PUT requests for an event

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            event = Event.objects.get(pk=pk)
            event.description = request.data["description"]
            event.date = request.data["date"]
            event.time = request.data["time"]

            game = Game.objects.get(pk=request.data["gameId"])
            event.game = game
            organizer = Gamer.objects.get(pk=request.data["organizerId"])
            event.organizer = organizer
            event.save()

            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except Event.DoesNotExist:
            return Response({'message': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        except Game.DoesNotExist:
            return Response({'message': 'Game not found'}, status=status.HTTP_404_NOT_FOUND)
        except Gamer.DoesNotExist:
            return Response({'message': 'Organizer not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response({'message': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk):
        """Handle DELETE requests for an event

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            event = Event.objects.get(pk=pk)
            event.delete()
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except Event.DoesNotExist:
            return Response({'message': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response({'message': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['post'], detail=True)
    def signup(self, request, pk):
        """Post request for a user to sign up for an event"""
        try:
            user_id = request.data.get("userId")
            if not user_id:
                return Response({'message': 'userId is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Use `uid` instead of `user_id`
            gamer = Gamer.objects.get(uid=user_id)
            event = Event.objects.get(pk=pk)

            attendee = EventGamer.objects.create(
                gamer=gamer,
                event=event
            )
            return Response({'message': 'Gamer added', 'attendee_id': attendee.id}, status=status.HTTP_201_CREATED)
        except Gamer.DoesNotExist:
            return Response({'message': 'Gamer not found'}, status=status.HTTP_404_NOT_FOUND)
        except Event.DoesNotExist:
            return Response({'message': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response({'message': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['delete'], detail=True)
    def leave(self, request, pk):
        """Delete request for a user to leave an event"""
        try:
            user_id = request.data.get("userId")
            if not user_id:
                return Response({'message': 'userId is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Use `uid` instead of `user_id`
            gamer = Gamer.objects.get(uid=user_id)
            # gamer = Gamer.objects.get(user=request.data["user_id"])
            event = Event.objects.get(pk=pk)

            # Find the event_gamer object
            event_gamer = EventGamer.objects.get(gamer=gamer, event=event)

            # Delete the gamer from the join table
            event_gamer.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except (Gamer.DoesNotExist, Event.DoesNotExist, EventGamer.DoesNotExist) as ex:
            return Response({'message': str(ex)}, status=status.HTTP_404_NOT_FOUND)


class EventSerializer(serializers.ModelSerializer):
    """JSON serializer for events"""
    joined = serializers.BooleanField(default=False)

    class Meta:
        model = Event
        fields = ('id', 'description', 'date',
                  'time', 'game_id', 'organizer_id', 'joined')
        depth = 2
