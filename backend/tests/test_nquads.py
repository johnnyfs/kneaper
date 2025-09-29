from datetime import datetime, timezone
from app.schemas import IRI, UID, Facet, Literal, NQuad, BlankNode


def test_nquad_rendering() -> None:
    nquads = [
        NQuad(
            subject=IRI("http://example.org/subject"),
            predicate=IRI("http://example.org/predicate"),
            object=Literal("object value"),
            facets=[
                Facet(key="facet1", value="value1"),
                Facet(key="facet2", value=2),
                Facet(key="facet3", value=3.0),
                Facet(key="facet4", value=True),
                Facet(key="facet5", value=datetime(2020, 1, 1, 12, 0, 0, tzinfo=timezone.utc)),
            ],
            graph=IRI("http://example.org/graph"),
        ),
        NQuad(
            subject=BlankNode("b1"),
            predicate=IRI("http://example.org/knows"),
            object=BlankNode("b2")
        ),
        NQuad(
            subject=UID("0x14e"),
            predicate=IRI("http://example.org/name"),
            object=UID("0x15f")
        ),
        NQuad(
            subject=BlankNode("b2"),
            predicate=IRI("http://example.org/name"),
            object=Literal("Alice", lang="en")
        ),
        NQuad(
            subject=BlankNode("b3"),
            predicate=IRI("http://example.org/age"),
            object=Literal(30)
        ),
        NQuad(
            subject=BlankNode("b3"),
            predicate=IRI("http://example.org/name"),
            object=Literal(datetime(2020, 1, 1, 12, 0, 0, tzinfo=timezone.utc), xsd="xsd:dateTime")
        )
    ]
    rendered = NQuad.render(nquads)
    assert isinstance(rendered, bytes)
    assert rendered.decode("utf-8").split("\n") == [
        """<http://example.org/subject> <http://example.org/predicate> "object value" (facet1="value1", facet2=2, facet3=3.0, facet4=true, facet5="2020-01-01T12:00:00Z") <http://example.org/graph> .""",
        """_:b1 <http://example.org/knows> _:b2 .""",
        """<0x14e> <http://example.org/name> <0x15f> .""",
        """_:b2 <http://example.org/name> "Alice"@en .""",
        """_:b3 <http://example.org/age> "30"^^<xsd:integer> .""",
        """_:b3 <http://example.org/name> "2020-01-01T12:00:00Z"^^<xsd:dateTime> .""",
        "",
    ]