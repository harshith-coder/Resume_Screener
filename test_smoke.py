import io
from resume_parser import extract_text_from_file
from matcher import match_with_weights
from feedback import save_feedback, list_feedback


class FakeUpload:
    def __init__(self, name, text):
        self.name = name
        self._b = text.encode('utf-8')

    def read(self):
        return self._b


def main():
    jd = """
    Looking for a Python developer with experience in machine learning, NLP, and REST APIs. Must know Python, pandas, and transformers.
    """

    resume_text = """
    Alice Example
    Experience: 3 years building NLP systems using Python, pandas, and PyTorch. Worked on REST APIs and microservices.
    Skills: Python, pandas, PyTorch, REST, Docker
    """

    f = FakeUpload('alice.txt', resume_text)
    parsed = extract_text_from_file(f)
    print('Parsed text (first 300 chars):')
    print(parsed.get('text','')[:300])

    score, details = match_with_weights(jd, parsed)
    print('\nMatch score:', score)
    print('Details:', details)

    # Save feedback
    save_feedback('alice.txt', jd, 5, 'Looks promising')
    print('\nRecent feedback:')
    for row in list_feedback(5):
        print(row)


if __name__ == '__main__':
    main()
