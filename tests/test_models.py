from app.db import Base


def test_expected_tables_exist() -> None:
    expected = {"users", "refresh_tokens", "posts", "post_revisions", "categories", "tags", "comments", "media", "post_categories", "post_tags", "newsletter_subscribers"}
    assert expected <= set(Base.metadata.tables)
