from django.core.management.base import BaseCommand

from api.models import KBEntry


KB_ENTRIES = [
    {
        "question": "What is select_related in Django ORM?",
        "answer": (
            "select_related performs a SQL JOIN and retrieves related "
            "foreign-key or one-to-one objects in the same database query."
        ),
        "category": KBEntry.Category.DATABASE,
    },
    {
        "question": "What is prefetch_related in Django ORM?",
        "answer": (
            "prefetch_related runs separate database queries and combines "
            "the results in Python. It is useful for many-to-many and "
            "reverse foreign-key relationships."
        ),
        "category": KBEntry.Category.DATABASE,
    },
    {
        "question": "How does transaction.atomic() work in Django?",
        "answer": (
            "transaction.atomic creates a database transaction block. "
            "All database operations inside the block are committed together, "
            "or rolled back if an exception occurs."
        ),
        "category": KBEntry.Category.DATABASE,
    },
    {
        "question": "When should I use Q objects in Django ORM?",
        "answer": (
            "Q objects are used for complex database queries involving OR, "
            "NOT, or grouped conditions. They can be combined using &, |, "
            "and ~ operators."
        ),
        "category": KBEntry.Category.DATABASE,
    },
    {
        "question": "What is a JWT access token?",
        "answer": (
            "A JWT access token is a signed credential used to authenticate "
            "API requests. It usually contains a user identifier and an "
            "expiration time."
        ),
        "category": KBEntry.Category.API,
    },
    {
        "question": "How is a JWT sent to an API?",
        "answer": (
            "A JWT is commonly sent in the HTTP Authorization header using "
            "the Bearer scheme: Authorization: Bearer <token>."
        ),
        "category": KBEntry.Category.API,
    },
    {
        "question": "What is REST API authentication?",
        "answer": (
            "REST API authentication verifies the identity of the client "
            "making a request. Common approaches include JWT tokens, API keys, "
            "OAuth, and session authentication."
        ),
        "category": KBEntry.Category.API,
    },
    {
        "question": "What is middleware in Django?",
        "answer": (
            "Django middleware is a component that processes requests before "
            "they reach a view and responses before they are returned to the "
            "client."
        ),
        "category": KBEntry.Category.FRAMEWORK,
    },
    {
        "question": "What are Django signals?",
        "answer": (
            "Django signals allow parts of an application to respond when "
            "certain actions occur, such as when a model instance is saved "
            "or deleted."
        ),
        "category": KBEntry.Category.FRAMEWORK,
    },
    {
        "question": "What is Docker used for?",
        "answer": (
            "Docker packages an application and its dependencies into "
            "containers, helping teams run software consistently across "
            "development and deployment environments."
        ),
        "category": KBEntry.Category.CLOUD,
    },
    {
        "question": "What is cloud infrastructure?",
        "answer": (
            "Cloud infrastructure includes computing, storage, networking, "
            "and managed services delivered through cloud providers."
        ),
        "category": KBEntry.Category.CLOUD,
    },
    {
        "question": "Why should API credentials be kept secret?",
        "answer": (
            "API credentials identify and authorize clients. Exposing them "
            "can allow unauthorized users to access protected services or "
            "consume another company's usage quota."
        ),
        "category": KBEntry.Category.GENERAL,
    },
]


class Command(BaseCommand):
    help = "Seed the knowledge base with initial Q&A entries."

    def handle(self, *args, **options):
        created_count = 0
        existing_count = 0

        for entry_data in KB_ENTRIES:
            _, created = KBEntry.objects.get_or_create(
                question=entry_data["question"],
                defaults={
                    "answer": entry_data["answer"],
                    "category": entry_data["category"],
                },
            )

            if created:
                created_count += 1
            else:
                existing_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Knowledge base seeding complete: "
                f"{created_count} created, "
                f"{existing_count} already existed."
            )
        )
