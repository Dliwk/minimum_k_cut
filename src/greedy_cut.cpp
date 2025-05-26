#include <iostream>
#include <vector>
#include <functional>
#include <algorithm>
#include <limits>
#include <tuple>
#include <cassert>
#include <chrono>
#include <random>
using namespace std;

struct dsu {
  vector<int> par, rng;

  dsu(int n) {
    par.resize(n);
    iota(par.begin(), par.end(), 0);
    rng.resize(n, 1);
  }

  int get(int v) {
    if (par[v] == v) {
      return v;
    }
    return par[v] = get(par[v]);
  }

  bool unite(int u, int v) {
    u = get(u), v = get(v);
    if (u == v) {
      return false;
    }
    if (rng[u] < rng[v]) {
      swap(u, v);
    }
    rng[u] += rng[v];
    par[v] = u;
    return true;
  }

};

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

  sort(edges.begin(), edges.end(),
       [](auto lhs, auto rhs) {
         return get<2>(lhs) > get<2>(rhs);
       });

  dsu components(n);
  vector<bool> erased(m, true);

  int comp_cnt = n;
  for (int i = 0; i < m; ++i) {
    int from = get<0>(edges[i]);
    int to = get<1>(edges[i]);
    if (components.unite(from, to)) {
      --comp_cnt;
    }
    if (comp_cnt < k) {
      break;
    }
    erased[i] = false;
  }

  long long mincut = 0;
  for (int i = 0; i < m; ++i) {
    if (erased[i]) {
      mincut += get<2>(edges[i]);
    }
  }

  std::cout << mincut << '\n';
  
}
