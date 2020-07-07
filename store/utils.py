import logging
import random
from rest_framework_simplejwt.tokens import RefreshToken


logger = logging.getLogger('django')


def id_generator(size=6):
    return "".join(str(random.randint(0, 9)) for _ in range(size))


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

