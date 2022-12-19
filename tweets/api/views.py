from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import TweetSerializer, TweetCreateSerializer
from tweets.models import Tweet


class TweetViewSet(viewsets.GenericViewSet,
                   viewsets.mixins.CreateModelMixin,
                   viewsets.mixins.ListModelMixin):
    """
    API endpoint that allows users to create, list tweets
    """
    queryset = Tweet.objects.all()
    serializer_class = TweetCreateSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        """
        重载 list 方法，不列出所有 tweets，必须要求指定 user_id 作为筛选条件
        """
        if 'user_id' not in request.query_params:
            return Response('missing user_id', status=400)

        # This is equivalent to SQL
        # select * from twitter_tweets
        # where user_id = xxx
        # order by created_at desc
        #
        user_id = request.query_params['user_id']
        tweets = Tweet.objects.filter(user_id=user_id).order_by('-created_at')
        serializer = TweetSerializer(tweets, many=True)
        # json format needs to be hashset, so needs to assign a key, here it will be tweets
        # json format cannot be list
        return Response({'tweets': serializer.data})

    def create(self, request, *args, **kwargs):
        """
        重载 create 方法，因为需要默认用当前登录用户作为 tweet.user
        """
        serializer = TweetCreateSerializer(
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': "Please check input",
                'errors': serializer.errors,
            }, status=400)
        tweet = serializer.save()
        return Response(TweetSerializer(tweet).data, status=201)