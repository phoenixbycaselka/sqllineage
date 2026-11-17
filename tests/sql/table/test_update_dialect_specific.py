import pytest

from ...helpers import assert_table_lineage_equal


@pytest.mark.parametrize("dialect", ["mysql"])
def test_update_with_join(dialect: str):
    assert_table_lineage_equal(
        "UPDATE tab1 a INNER JOIN tab2 b ON a.col1=b.col1 SET a.col2=b.col2",
        {"tab2"},
        {"tab1"},
        dialect=dialect,
    )


@pytest.mark.parametrize("dialect", ["tsql"])
def test_update_with_specifying_a_table_alias_as_the_target_object(dialect: str):
    """
    tsql allows table alias to be followed after UPDATE keyword.

    See https://learn.microsoft.com/en-us/sql/t-sql/queries/update-transact-sql?view=sql-server-ver16#l-specifying-a-table-alias-as-the-target-object
    for reference.
    """
    assert_table_lineage_equal(
        """UPDATE sr  
SET sr.Name += ' - tool malfunction'  
FROM Production.ScrapReason AS sr  
JOIN Production.WorkOrder AS wo   
     ON sr.ScrapReasonID = wo.ScrapReasonID  
     AND wo.ScrappedQty > 300; """,
        {"Production.WorkOrder"},
        {"Production.ScrapReason"},
        dialect=dialect,
        test_sqlparse=False,
    )


@pytest.mark.parametrize("dialect", ["tsql"])
@pytest.mark.parametrize(
    "alias, alias_in_from", [("SR", "SR"), ("SR", "sr"), ("[sr]", "[sr]")]
)
def test_update_with_table_alias_as_target_object_case_and_quote(
    dialect: str, alias: str, alias_in_from: str
):
    """
    unquoted alias is case-insensitive and [sr] is the same alias as sr,
    the alias after UPDATE should still resolve to the table in FROM clause
    """
    assert_table_lineage_equal(
        f"""UPDATE {alias}
SET {alias}.Name = wo.Name
FROM Production.ScrapReason AS {alias_in_from}
JOIN Production.WorkOrder AS wo
     ON {alias_in_from}.ScrapReasonID = wo.ScrapReasonID""",
        {"Production.WorkOrder"},
        {"Production.ScrapReason"},
        dialect=dialect,
        test_sqlparse=False,
    )
