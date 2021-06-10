import { Resource } from 'kolibri.lib.apiResource';
import urls from 'kolibri.urls';

export default new Resource({
  name: 'zim',
  search(zim_filename, { query, start, max_results, suggest }) {
    const url = urls.zim_search(zim_filename);
    return this.client({
      url,
      method: 'get',
      params: { query, start, max_results, suggest },
    });
  },
});
