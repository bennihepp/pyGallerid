def bootstrap():
    from persistent.mapping import PersistentMapping
    return PersistentMapping()

def appmaker(zodb_root):
    if not 'gallery-app-root' in zodb_root:
        app_root = bootstrap()
        zodb_root['gallery-app-root'] = app_root
        import transaction
        transaction.commit()
    return zodb_root['gallery-app-root']
