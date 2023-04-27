
# MailtrainAPI

MailtrainAPI is a Python wrapper for the Mailtrain API (https://github.com/Mailtrain-org/mailtrain)

## Usage

```python
from mailtrain import Mailtrain

mt = Mailtrain("MAILTRAIN_API_KEY", "https://exemple.com")

all_lists_of_email = mt.get_lists("test@test.com")

all_subsribers = mt.get_subscribers("LIST_ID")

mt.add_subscriber("test@test.com", "LIST_ID", "Test", "Testovich")

```




