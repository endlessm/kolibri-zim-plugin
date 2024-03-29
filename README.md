# Kolibri Zim plugin

This is a Kolibri plugin to add a Zim file viewer.

![Kolibri Zim plugin showing Wikipedia](https://raw.githubusercontent.com/endlessm/kolibri-zim-plugin/v1.0.0/docs/images/wikipedia-index.png)

## Usage

Install a release from pypi:

    pip install kolibri-zim-plugin[full]

If you are using Kolibri 0.14.7, upgrade its bundled le-utils to the newest (unstable) version:

    pip install git+https://github.com/learningequality/le-utils.git@master --target=$(python3 -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')/kolibri/dist --upgrade

Enable the plugin in Kolibri:

    kolibri plugin enable kolibri_zim_plugin

Now, Zim content in Kolibri will be rendered using the Zim plugin.

For some example content, try adding the Wikipedia channel, either from Kolibri's user interface (you can use the channel token `nurob-nikis`) or with a management command:

    kolibri manage importchannel network f62db29be20453c4a267132e93a9e602
    kolibri manage importcontent network f62db29be20453c4a267132e93a9e602

## Development

### Getting started

Create a pipenv shell and then install additional dependencies using `bootstrap.sh`:

    pipenv shell
    ./scripts/bootstrap.sh

Install kolibri-zim-plugin in editable mode:

    pip install -e .

To build front end code:

    yarn build

Refer to the [Usage instructions](#Usage) to upgrade le-utils and enable the plugin.

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
