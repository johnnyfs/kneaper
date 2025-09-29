from datetime import datetime
from pydantic import BaseModel

# I created these to enforce syntax for mutations before realing
#  - Arcade tools do not support Union types.
#  - The gpt5-mini produces reliably valid syntax.
# Keeping them since they are already validated and might be useful
# as guiderails for cheaper models.

class UID(BaseModel):
    uid: str

    def to_bytes(self) -> bytes:
        return f"<{self.uid}>".encode("utf-8")

class IRI(BaseModel):
    iri: str

    def to_bytes(self) -> bytes:
        return f"<{self.iri}>".encode("utf-8")

class BlankNode(BaseModel):
    label: str

    def to_bytes(self) -> bytes:
        return f"_:{self.label}".encode("utf-8")

NodeRef = UID | IRI | BlankNode


class Literal(BaseModel):
    value: str # | int | float | bool | datetime
    xsd: str | None = None    # e.g. "xsd:string", "xsd:integer", "xsd:dateTime"
    lang: str | None = None   # e.g. "en", "fr"

    def to_bytes(self) -> bytes:
        if isinstance(self.value, datetime):
            s = self.value.isoformat().replace("+00:00", "Z")
            lit = self._quote(s)
            dtype = self.xsd or "xsd:dateTime"
            return f'{lit}^^<{dtype}>'.encode("utf-8")
        if isinstance(self.value, bool):
            v = "true" if self.value else "false"
            if self.xsd:  # allow explicit xsd:boolean
                return f'"{v}"^^<{self.xsd}>'.encode("utf-8")
            return f'"{v}"^^<xsd:boolean>'.encode("utf-8")
        if isinstance(self.value, (int, float)):
            s = str(self.value)
            if self.xsd:
                return f'"{s}"^^<{self.xsd}>'.encode("utf-8")
            # default numeric types
            kind = "xsd:integer" if isinstance(self.value, int) else "xsd:double"
            return f'"{s}"^^<{kind}>'.encode("utf-8")
        # string
        lit = self._quote(self.value)
        if self.lang:
            return f"{lit}@{self.lang}".encode("utf-8")
        if self.xsd:
            return f"{lit}^^<{self.xsd}>".encode("utf-8")
        return lit.encode("utf-8")

    @classmethod
    def _quote(cls, s: str) -> str:
        # minimal N-Quads escaping for double-quoted strings
        s = s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r")
        return f'"{s}"'


class Facet(BaseModel):
    key: str
    value: str # | int | float | bool | datetime

    def to_bytes(self) -> bytes:
        v = self.value
        if isinstance(v, datetime):
            v = v.isoformat().replace("+00:00", "Z")
        if isinstance(v, str):
            # quote + escape for strings
            v = Literal._quote(v)
            return f"{self.key}={v}".encode("utf-8")
        if isinstance(v, bool):
            return f"{self.key}={'true' if v else 'false'}".encode("utf-8")
        # numbers unquoted
        return f"{self.key}={v}".encode("utf-8")


class NQuad(BaseModel):
    subject: IRI # NodeRef
    predicate: IRI
    object: Literal # NodeRef | Literal
    facets: list[Facet] | None = None
    graph: IRI | None = None

    def to_chunks(self) -> list[bytes]:
        chunks = [self.subject.to_bytes(), b" ", self.predicate.to_bytes(), b" ", self.object.to_bytes()]
        if self.facets and len(self.facets) > 0:
            chunks.append(b" (")
            for facet in self.facets[:-1]:
                chunks.extend([facet.to_bytes(), b", "])
            chunks.append(self.facets[-1].to_bytes())
            chunks.append(b")")
        if self.graph:
            chunks.extend([b" ", self.graph.to_bytes()])
        chunks.append(b" .\n")
        return chunks
    
    @classmethod
    def render(cls, nquads: list['NQuad']) -> bytes:
        return b"".join(chunk for nquad in nquads for chunk in nquad.to_chunks())
