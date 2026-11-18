from django.db import connection
from .contracts import Receipt, ProviderFailure


class MockProvider:
    """Fixed synthetic usage, no sockets, tools, prompts or hidden state authority."""
    provider_id='mock-a'

    def generate(self,request,dispatch_id):
        if connection.in_atomic_block:
            raise RuntimeError('Provider dispatch inside database transaction')
        request.validate()
        units=min(request.max_input,10)+min(request.max_output,10)
        return Receipt('mock.'+str(dispatch_id),min(request.max_input,10),0,min(request.max_output,10),0,units,'mock-v1')

    def cancel(self,dispatch_id):
        if connection.in_atomic_block:
            raise RuntimeError('Provider cancellation inside database transaction')
        return {'dispatch_id':str(dispatch_id),'status':'cancel_requested'}


class AlternateMockProvider(MockProvider):
    provider_id='mock-b'
