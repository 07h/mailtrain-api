
# MailtrainAPI

MailtrainAPI is an async Python wrapper for the Mailtrain API (https://github.com/Mailtrain-org/mailtrain)

## Usage

```python
from mailtrain import Mailtrain

mt = Mailtrain("MAILTRAIN_API_KEY", "https://exemple.com")

all_lists_of_email = await mt.get_lists("test@test.com")

all_subsribers = await mt.get_subscribers("LIST_ID")

await mt.add_subscription("test@test.com", "LIST_ID", "Test", "Testovich")

```




