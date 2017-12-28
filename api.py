import hug

import songfortune as sf


@hug.cli()
def songfortune():
    return sf.main()


@hug.get('/')
def index():
    return {'message': songfortune()}


@hug.cli()
@hug.get('/refresh')
def refresh():
    try:
        sf.data_utils.refresh_cache()
        return {'success': True}
    except:
        return {'success': False}
