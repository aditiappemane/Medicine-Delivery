from fastapi import APIRouter

router = APIRouter(prefix="/help", tags=["help"])

@router.get("/faqs")
def get_faqs():
    """Return frequently asked questions and medical guidance."""
    return {
        "faqs": [
            {
                "question": "What should I do if my medicine is out of stock?",
                "answer": "You can search for alternatives or contact your pharmacy for assistance."
            },
            {
                "question": "How do I upload a prescription?",
                "answer": "Go to the Prescriptions section and use the upload button to submit your prescription image."
            },
            {
                "question": "What if I need urgent medicine delivery?",
                "answer": "Use the Emergency Delivery feature for prioritized service."
            },
            {
                "question": "How do I get reminders for my medicines?",
                "answer": "Enable push notifications and set reminders in your profile or medicine list."
            },
            {
                "question": "How can elderly users get help?",
                "answer": "We offer large fonts, voice search, and a helpline for elderly users. Contact support for more."
            }
        ]
    } 