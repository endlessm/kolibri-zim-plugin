# Kolibri Zim plugin

This is a Kolibri plugin to add a Zim file viewer.

## Creating test content (very temporary hack)

Create a pipenv shell:

    pipenv install
    pipenv shell

Enable kolibri_zim_plugin:

    pip install -e .
    kolibri plugin enable kolibri_zim_plugin

Start Kolibri:

    kolibri start

Override Kolibri's le_utils with our own version:

    pip install git+https://github.com/dylanmccall/le-utils.git@add-zim-constants --target=$(python3 -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')/kolibri/dist --upgrade

Download a Wikipedia zim file to Kolibri's storage directory:

    mkdir -p ~/.kolibri/content/storage/0/0
    curl -L 'https://dumps.wikimedia.org/kiwix/zim/wikipedia/wikipedia_en_100_maxi_2021-05.zim' > ~/.kolibri/content/storage/0/0/00abcdef000000000000000000000000.zim

Install the "Canal de Patatas" channel:

    kolibri manage importchannel network 2f74713b89595a1899a850df897bd7bb
    kolibri manage importcontent network 2f74713b89595a1899a850df897bd7bb

Edit "Growing potatoes" in "Canal de Patatas" (2f74713b89595a1899a850df897bd7bb)

    from kolibri.core.content.models import ContentNode, LocalFile
    node = ContentNode.objects.get(id='ad33938ca05a53a6bdf5e79944f12757')
    file = node.files.get(thumbnail=False)
    new_local_file = LocalFile(
        id='00abcdef000000000000000000000000',
        extension='zim',
        available=True,
        file_size=None
    )
    new_local_file.save()
    file.local_file = new_local_file
    file.preset = 'zim'
    file.save()

Navigate to <http://localhost:8080/en/learn/#/topics/c/ad33938ca05a53a6bdf5e79944f12757>
