import hug

import songfortune as sf


@hug.cli()
def songfortune():
    return sf.main()


@hug.get('/')
def index():
    return {'message': songfortune()}


@hug.cli()
def refresh():
    try:
        sf.data_utils.refresh_cache()
        return 'Cache refresh succeeded.'
    except:
        return 'Cache refresh failed.'
