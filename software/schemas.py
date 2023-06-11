import os
from rdflib import Graph, URIRef, RDFS, RDF


class Schemas():

    def __init__(self, paths, domain: list[str] = [str(RDFS.domain)], range: list[str] = [str(RDFS.range)]):
        # Load schemas from config into a graph
        self.graph = Graph()
        queue = paths.copy()
        for s in queue:
            if os.path.isdir(s):
                for f in os.listdir(s):
                    self.graph.parse(os.path.join(s, f))
            elif os.path.isfile(s):
                self.graph.parse(s)
            else:
                raise Exception(f'Warning: {s} is not a file or directory')

        # Maps IRIs of objects to a list of all their predecessors.
        # Used to build the breadcrumbs
        self.predecessors = {
            str(s): [str(o) for o in self.graph.objects(s, RDFS.subClassOf)] for s in self.graph.subjects(RDFS.subClassOf, None)
        }

        self.domain = domain
        self.range = range

    """ Get all classes for a given URI """
    def get_classes(self, iri: str) -> list[str]:
        return [o for o in self.graph.objects(URIRef(iri), RDF.type)]
    
    def get_properties_for_class(self, class_iri: str) -> list[str]:
        result = []
        for domain in self.domain:
            result += [s for s in self.graph.subjects(URIRef(domain), URIRef(class_iri))]
        return result
    
    def get_range(self, iri: str) -> list[str]:
        result = []
        for range in self.range:
            result += [o for o in self.graph.objects(URIRef(iri), URIRef(range))]
        return result
    
    def get_subclasses(self, iri: str) -> list[str]:
        return [s for s in self.graph.subjects(RDFS.subClassOf, URIRef(iri))]

    def get_breadcrumbs(self, id: str):
        if id not in self.predecessors:
            return [[id]]
        ps = [p for p in self.predecessors[id] if p is not id]
        if len(ps) == 0:
            return [[id]]

        breadcrumbs = []
        for parent in self.predecessors[id]:
            for bc in self.get_breadcrumbs(parent):
                bc.extend([id])
                breadcrumbs.append(bc)
        return breadcrumbs
