#include <algorithm>
#include <cassert>
#include <functional>
#include <iostream>
#include <limits>
#include <tuple>
#include <vector>
using namespace std;

template <class T> struct flow_network {
  int n;
  vector<vector<int>> adj;

  struct E {
    int from, to;
    T capacity, flow;
  };

  vector<E> edge;

  T flow = 0;

  flow_network(int n) : n(n), adj(n) {}

  void clear_flow() {
    for (auto &e : edge)
      e.flow = 0;
    flow = 0;
  }

  int insert(int from, int to, T forward_cap, T backward_cap) {
    int ind = (int)edge.size();
    adj[from].push_back(ind);
    edge.push_back({from, to, forward_cap, 0});
    adj[to].push_back(ind + 1);
    edge.push_back({to, from, backward_cap, 0});
    return ind;
  }

  void add_flow(int i, T f) {
    edge[i].flow += f;
    edge[i ^ 1].flow -= f;
  }
};

template <class T> struct dinic_maximum_flow {
  static constexpr T eps = (T)1e-9, inf = numeric_limits<T>::max();

  flow_network<T> &F;

  dinic_maximum_flow(flow_network<T> &F) : F(F), ptr(F.n), level(F.n), q(F.n) {}

  vector<int> ptr, level, q;

  bool bfs(int source, int sink) {
    fill(level.begin(), level.end(), -1);
    q[0] = sink;
    level[sink] = 0;
    int beg = 0, end = 1;
    while (beg < end) {
      int i = q[beg++];
      for (auto ind : F.adj[i]) {
        auto &e = F.edge[ind];
        auto &re = F.edge[ind ^ 1];
        if (re.capacity - re.flow > eps && level[e.to] == -1) {
          level[e.to] = level[i] + 1;
          if (e.to == source)
            return true;
          q[end++] = e.to;
        }
      }
    }
    return false;
  }

  T dfs(int u, T w, int sink) {
    if (u == sink)
      return w;
    int &j = ptr[u];
    while (j >= 0) {
      int ind = F.adj[u][j];
      auto &e = F.edge[ind];
      if (e.capacity - e.flow > eps && level[e.to] == level[u] - 1) {
        T flow = dfs(e.to, min(e.capacity - e.flow, w), sink);
        if (flow > eps) {
          F.add_flow(ind, flow);
          return flow;
        }
      }
      --j;
    }
    return 0;
  }

  T maximum_flow(int source, int sink) {
    while (bfs(source, sink)) {
      for (auto i = 0; i < F.n; ++i) {
        ptr[i] = (int)F.adj[i].size() - 1;
      }
      T sum = 0;
      while (true) {
        T add = dfs(source, inf, sink);
        if (add <= eps)
          break;
        sum += add;
      }
      if (sum <= eps)
        break;
      F.flow += sum;
    }
    return F.flow;
  }

  auto minimum_cut(int source, int sink) {
    T cut_weight = maximum_flow(source, sink);
    vector<int> left, right;
    for (auto u = 0; u < F.n; ++u) {
      (!~level[u] ? left : right).push_back(u);
    }
    return tuple{cut_weight, left, right};
  }
};

template <class T>
vector<tuple<int, int, T>>
gomory_hu_tree(int n, const vector<tuple<int, int, T>> &edge) {
  flow_network<T> F(n);
  for (auto &[u, v, w] : edge)
    F.insert(u, v, w, w);

  vector<tuple<int, int, T>> res(max(n - 1, 0));
  vector<int> pv(n), cut(n);

  for (auto i = 1; i < n; ++i) {
    F.clear_flow();
    auto [flow, left, right] = dinic_maximum_flow<T>(F).minimum_cut(pv[i], i);
    fill(cut.begin(), cut.end(), 0);
    for (auto u : right)
      cut[u] = 1;
    for (auto j = i + 1; j < n; ++j) {
      if (cut[j] == cut[i] && pv[j] == pv[i])
        pv[j] = i;
    }
    res[i - 1] = {pv[i], i, flow};
  }
  return res;
}

int main() {
  ios_base::sync_with_stdio(0);
  cin.tie(nullptr);
  int n, m, k;
  cin >> n >> m >> k;
  vector<tuple<int, int, long long>> edges(m);
  for (auto &[u, v, w] : edges) {
    cin >> u >> v >> w;
    --u, --v;
  }

  auto tree_edges = gomory_hu_tree(n, edges);
  sort(tree_edges.begin(), tree_edges.end(),
       [](auto lhs, auto rhs) { return get<2>(lhs) < get<2>(rhs); });

  vector<vector<int>> graph(n);
  for (int i = k - 1; i < tree_edges.size(); ++i) {
    int from = get<0>(tree_edges[i]);
    int to = get<1>(tree_edges[i]);
    graph[from].push_back(to);
    graph[to].push_back(from);
  }

  vector<int> component(n, -1);
  function<void(int, int)> dfs;

  dfs = [&](int v, int color) {
    component[v] = color;
    for (int adj : graph[v]) {
      if (component[adj] == -1) {
        dfs(adj, color);
      }
    }
  };

  int color = 0;
  for (int v = 0; v < n; ++v) {
    if (component[v] == -1) {
      dfs(v, color++);
    }
  }

  assert(color >= k);

  long long mincut = 0;
  for (auto [u, v, w] : edges) {
    if (component[u] != component[v]) {
      mincut += w;
    }
  }

  cout << mincut << '\n';
}