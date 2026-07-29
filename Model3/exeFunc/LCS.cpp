#include <iostream>
#include <vector>
#include <string>
#include <algorithm>

using namespace std;
vector<vector<int>> dp;

int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string s1,s2; cin >> s1 >> s2;
    int n = s1.length(),m = s2.length();

    dp.assign(n+5,vector<int>(m+5,0));
    
    for (int i = 0; i < n; i++){
        for (int j = 0; j < m; j++){
            if (s1[i] == s2[j])
                dp[i+1][j+1] = dp[i][j] + 1;
            else
                dp[i+1][j+1] = max(dp[i][j+1],dp[i+1][j]);
        }
    }
    cout << dp[n][m];
    return 0;
}

//ABCDEFG
//BAKCDEGFG