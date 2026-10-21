def slugify(text, max_length=50):
    """문자열을 URL용 slug로 바꾼다.

    - 소문자로 바꾼다
    - 영문 소문자와 숫자가 아닌 문자는 모두 하이픈(-)으로 바꾼다
    - 하이픈이 연달아 나오면 하나로 줄인다
    - 앞뒤 하이픈은 제거한다
    - 결과가 max_length보다 길면 max_length까지 자르고, 끝에 남은 하이픈은 제거한다
    예: slugify("Hello, World!") == "hello-world"
    """
    raise NotImplementedError
