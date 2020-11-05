from ibm_cloud_sdk_core.authenticators import BearerTokenAuthenticator, IAMAuthenticator, Authenticator
from argparse import Namespace

def choose_auth(args: Namespace) -> Authenticator:
    """
    Choose the authenticator type

    :param args:
    :return:
    """
    if args.auth_type == 'iam':
        return IAMAuthenticator(args.iam_apikey)
    elif args.auth_type == 'bearer':
        return BearerTokenAuthenticator(args.iam_apikey)
    else:
        raise ValueError(f'Unknown auth type: "{args.auth_type}"')