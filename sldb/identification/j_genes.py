from Bio import SeqIO

class JGermlines(dict):
    def __init__(self, path_to_germlines, upstream_of_cdr3, anchor_len,
                 min_anchor_len):
        self._upstream_of_cdr3 = upstream_of_cdr3
        self._anchor_len = anchor_len
        self._min_anchor_len = min_anchor_len

        with open(path_to_germlines) as fh:
            for record in SeqIO.parse(fh, 'fasta'):
                assert record.id.startswith('IGHJ')
                if all(map(lambda c: c in 'ATCG', record.seq)):
                    self[record.id] = str(record.seq).upper()

        self._anchors = {name: seq[-anchor_len:] for name, seq in
            self.iteritems()}

    @property
    def upstream_of_cdr3(self):
        return self._upstream_of_cdr3

    @property
    def anchor_len(self):
        return self._anchor_len

    @property
    def full_anchors(self):
        return self._anchors

    def get_j_in_cdr3(self, gene):
        return self[gene][:-self._upstream_of_cdr3]

    def get_all_anchors(self, limit_genes=None):
        if limit_genes is None:
            limit_genes = self
        max_len = max(map(len, limit_genes.values()))
        for trim_len in range(0, max_len, 3):
            for j, seq in self.iteritems():
                trimmed_seq = seq[-self.anchor_len:-trim_len]
                if len(trimmed_seq) >= self._min_anchor_len:
                    yield trimmed_seq, trim_len, j

    def get_ties(self, name, seq):
        tied = set([name])
        for j, other_seq in sorted(self.iteritems()):
            if other_seq[-self.anchor_len:][:len(seq)] == seq:
                tied.add(j)
        return tied