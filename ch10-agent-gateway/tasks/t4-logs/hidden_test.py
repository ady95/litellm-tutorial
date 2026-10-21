from log_report import summarize


def test_report(tmp_path):
    r = summarize("access.log")
    assert r["total"] == 6
    assert r["status"] == {"200": 3, "429": 1, "500": 1, "503": 1}
    assert r["errors"] == 2
    assert r["top_path"] == "/v1/chat/completions"


def test_tie_breaks_alphabetically(tmp_path):
    p = tmp_path / "a.log"
    p.write_text(
        '1.1.1.1 - - [21/Oct/2026:10:00:01 +0900] "GET /b HTTP/1.1" 200 1\n'
        '1.1.1.1 - - [21/Oct/2026:10:00:02 +0900] "GET /a HTTP/1.1" 404 1\n'
    )
    r = summarize(str(p))
    assert r["top_path"] == "/a"
    assert r["errors"] == 0
