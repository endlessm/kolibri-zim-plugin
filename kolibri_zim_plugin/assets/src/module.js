import ContentRendererModule from 'content_renderer_module';
import ZimComponent from './views/ZimRendererIndex';

class ZimModule extends ContentRendererModule {
  get rendererComponent() {
    return ZimComponent;
  }
}

const zimModule = new ZimModule();

export { zimModule as default };
