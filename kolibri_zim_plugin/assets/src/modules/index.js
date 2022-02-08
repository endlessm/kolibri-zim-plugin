const DEFAULT_NAVIGATION_HISTORY = [
  {
    path: '',
    title: '',
  },
];

export default {
  namespaced: true,
  state: {
    navigationHistory: DEFAULT_NAVIGATION_HISTORY.slice(),
  },
  mutations: {
    SET_NAVIGATION_HISTORY(state, navigationHistory) {
      state.navigationHistory = navigationHistory;
    },
  },
  getters: {},
  actions: {
    pushNavigationHistory(store, { path, redirectFrom, title }) {
      const navigationHistory = store.state.navigationHistory.slice();

      if (redirectFrom === '') {
        // Special case to treat the index page's path as "", which makes it
        // easier to have a persistent Home breadcrumb.
        path = '';
      }

      const existingIndex = navigationHistory.findIndex(
        entry => entry.path === path || entry.path === redirectFrom
      );

      if (existingIndex >= 0) {
        navigationHistory.splice(existingIndex);
      }
      navigationHistory.push({ path, title });
      store.commit('SET_NAVIGATION_HISTORY', navigationHistory);
    },
    resetNavigationHistory(store) {
      store.commit('SET_NAVIGATION_HISTORY', DEFAULT_NAVIGATION_HISTORY.slice());
    },
  },
};
