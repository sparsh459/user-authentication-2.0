from django.contrib.auth.tokens import PasswordResetTokenGenerator

from six import text_type
# will generate tokens
class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self,user,timestamp):
        return (
            # uniques string to activate teh account
        text_type(user.pk) + text_type(timestamp) 
        # text_type(user.profile.signup_confirmation)
        )

generate_token = TokenGenerator()