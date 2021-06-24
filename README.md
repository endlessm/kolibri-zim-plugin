# Kolibri Zim plugin

This is a Kolibri plugin to add a Zim file viewer.

![Kolibri Zim plugin showing Wikipedia](https://raw.githubusercontent.com/endlessm/kolibri-zim-plugin/v1.0.0/docs/images/wikipedia-index.png)

## Usage

Install a release from pypi:

    pip install kolibri-zim-plugin

Enable the plugin in Kolibri:

    kolibri plugin enable kolibri_zim_plugin

Now, Zim content in Kolibri will be rendered using the Zim plugin.

## Development

### Getting started

Create a pipenv shell and then install additional dependencies using `bootstrap.sh`:

    pipenv shell
    ./scripts/bootstrap.sh

Install kolibri-explore-plugin in editable mode:

    pip install -e .

To build front end code:

    yarn build

### Submitting changes

Before submitting changes, please be sure to run the pre-commit checks:

    pre-commit run

If you can configure git to run these checks automatically:

    pre-commit install -f --install-hooks

## Creating a release

If you are releasing a new version, use `bump-version` with with `major`, `minor`, or `patch`. For example:

    yarn bump-version patch

This creates a new commit and a git tag. Push this to the remote:

    git push
    git push --tags

Create a `.whl` file:

    yarn dist

The file will be placed in the `dist/` directory.

Finally, upload the `.whl` file to PyPi:

    yarn release

## Creating test content

This is a temporary hack to add Zim content to Kolibri, after installing and enabling kolibri-zim-plugin.

Override Kolibri's le_utils with the newest version:

    pip install git+https://github.com/learningequality/le-utils.git@master --target=$(python3 -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')/kolibri/dist --upgrade

Download a Wikipedia zim file to Kolibri's storage directory:

    mkdir -p ~/.kolibri/content/storage/0/0
    curl -L 'http://download.kiwix.org/zim/wikipedia/wikipedia_en_all_mini_2021-01.zim' > ~/.kolibri/content/storage/0/0/00abcdef000000000000000000000000.zim

> The `wikipedia_en_all_mini_2021-01.zim` zim file is 11 GB. If you need to save space, download `wikipedia_en_100_maxi_2021-05.zim` instead.

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

Navigate to <http://localhost:8080/en/learn/#/topics/c/ad33938ca05a53a6bdf5e79944f12757>.
