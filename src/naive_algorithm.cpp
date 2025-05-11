#include <iostream>
#include <unordered_map>
#include <vector>

using namespace std;

using ll = long long;
using ii = pair<ll, ll>;
using vi = vector<ll>;
using vii = vector<ii>;
using vvi = vector<vi>;
using vvii = vector<vii>;

int main() {
  ll n, m, k;
  cin >> n >> m >> k;

  vvii gr(n);
  for (int i = 0; i < m; ++i) {
    ll u, v, w;
    cin >> u >> v >> w;
    --u, --v;
    gr[u].emplace_back(v, w);
    gr[v].emplace_back(u, w);
  }

  std::unordered_map<ll, vi> dp;

  auto partition_cost = [&](ll set1, ll set2) {
    ll result = 0;
    for (ll u = 0; u < n; ++u) {
      if (bool in_set1 = ((1ll << u) & set1); !in_set1) {
        continue;
      }
      for (auto [v, w] : gr[u]) {
        if (bool in_set2 = ((1ll << v) & set2); !in_set2) {
          continue;
        }
        result += w;
      }
    }
    return result;
  };

  for (ll mask = 0; mask < (1ll << n); ++mask) {
    for (ll submask = (mask - 1) & mask; submask;
         submask = (submask - 1) & mask) {
      auto submask2 = mask & ~submask;
      if (!dp.count(mask)) {
        dp[mask] = vi(k, 1e18);
        dp[mask][0] = 0;
      }
      if (!dp.count(submask2)) {
        dp[submask2] = vi(k, 1e18);
        dp[submask2][0] = 0;
      }
      ll cost = partition_cost(submask, submask2);
      for (ll l = 1; l < k; ++l) {
        dp[mask][l] = min(dp[mask][l], cost + dp[submask2][l - 1]);
      }
    }
  }

  cout << dp[(1ll << n) - 1][k - 1] << endl;
}

/*

3 3 3
1 2 1
1 3 2
2 3 3


3 3 2
1 2 1
1 3 2
2 3 3

3 3 2
1 2 3
1 3 3
2 3 3


*/