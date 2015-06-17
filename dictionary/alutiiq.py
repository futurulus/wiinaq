def get_root(word):
    endings = ['luni', 'lutek', 'luteng', 'kunani', 'kunatek', 'kunateng',
               'luku', 'lukek', 'luki', 'kunaku', 'kunakek', 'kunaki']
    for ending in endings:
        if ending.startswith('l') and word.endswith('l' + ending):
            return word[:-len(ending) - 1] + 't'
        if ending.startswith('k') and word.endswith('g' + ending):
            return word[:-len(ending) - 1]
        if word.endswith(ending):
            return word[:-len(ending)]
    
    neg_endings = ['inani', 'inatek', 'inateng', 'inaku', 'inakek', 'inaki']
    for ending in neg_endings:
        if word.endswith(ending):
            return word[:-len(ending)] + 'it'

    if word.endswith('q'):
        return word[:-1] + 'r'

    return word


def apply_transformations(before, center, after):
    if after is not None:
        if after.startswith('-'):
            center = get_root(center)
            if center[-1] not in 'aeiou':
                center = center[:-1]
        elif after.startswith('~'):
            center = get_root(center)
            if center.endswith('r'):
                center = center[:-1]
        elif after.startswith('+'):
            center = get_root(center)

    if before is not None:
        if center.startswith('~k'):
            if before.endswith('r'):
                center = 'q' + center[2:]
            else:
                center = center[1:]
        elif center[0] in '+-~':
            center = center[1:]
        else:
            center = ' ' + center

    return center


def morpho_join(chunks):
    chunks = [None] + chunks + [None]
    transformed = []
    for i in range(1, len(chunks) - 1):
        transformed.append(apply_transformations(chunks[i - 1],
                                                 chunks[i],
                                                 chunks[i + 1]))
    return ''.join(transformed)
