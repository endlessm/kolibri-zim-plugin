import store from 'kolibri.coreVue.vuex.store';
import ContentRendererModule from 'content_renderer_module';
import ZimComponent from './views/ZimRendererIndex';
import storeModule from './modules';

class ZimModule extends ContentRendererModule {
  get rendererComponent() {
    return ZimComponent;
  }

  get store() {
    return store;
  }

  ready() {
    this.store.registerModule('zim', storeModule);
  }
}

const zimModule = new ZimModule();

export { zimModule as default };
