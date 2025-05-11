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

vi digits(ll mask3, ll n) {
  vi result;

  for (int i = 0; i < n; ++i) {
    ll digit = mask3 % 3;
    mask3 /= 3;
    result.emplace_back(digit);
  }

  return vi(result.rbegin(), result.rend());
}

tuple<ll, ll, ll> split(ll mask3, ll n) {
  ll mask1 = 0;
  ll mask2 = 0;
  ll mask12 = 0;
  for (auto digit : digits(mask3, n)) {
    mask1 *= 2;
    mask2 *= 2;
    mask12 *= 2;

    if (digit == 1) {
      mask1 += 1;
      mask12 += 1;
    } else if (digit == 2) {
      mask2 += 1;
      mask12 += 1;
    }
  }
  return {mask1, mask2, mask12};
}

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

  ll max_mask_3 = 1;
  for (int i = 0; i < n; ++i) {
    max_mask_3 *= 3;
  }
  for (ll mask3 = 0; mask3 < max_mask_3; ++mask3) {
    auto [subset1, subset2, set] = split(mask3, n);
    if (subset1 == 0 || subset2 == 0) {
      continue;
    }
    if (!dp.count(set)) {
      dp[set] = vi(k, 1e18);
      dp[set][0] = 0;
    }
    if (!dp.count(subset2)) {
      dp[subset2] = vi(k, 1e18);
      dp[subset2][0] = 0;
    }
    ll cost = partition_cost(subset1, subset2);
    for (ll l = 1; l < k; ++l) {
      dp[set][l] = min(dp[set][l], cost + dp[subset2][l - 1]);
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