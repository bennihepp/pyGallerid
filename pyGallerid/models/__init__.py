def bootstrap_db():
    import gallery
    return gallery.Gallery('Photography by Benjamin Hepp')
    #from persistent.mapping import PersistentMapping
    #return PersistentMapping()

def appmaker(zodb_root):
    if not 'pyGallerid-app-root' in zodb_root:
        app_root = bootstrap_db()
        zodb_root['pyGallerid-app-root'] = app_root
        import transaction
        transaction.commit()
    return zodb_root['pyGallerid-app-root']
