#include <iostream>
#include <vector>

using namespace std;

vector<vector<float>> v;
vector<vector<int>> image;

/*
This file is a function for down-sampling image to 100*100 int metric.
Making it require only 0.32 MB for contain each picture after down-sampling.
*/

int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n,m; cin >> n >> m;
    image.assign(n+5,vector<int>(m+5,0));
    v.assign(100+5,vector<float>(100+5,-1));

    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++)
            cin >> image[i][j];

    //size of Down_Sampled pixel
    int N = n/100;
    int M = m/100;

    //Down sampling
    for (int i = 0; i < 100; i++){
        for (int j = 0; j < 100; j++ ){
            float k = 0;
            for (int I = i*N ; I < i*N; I++){
                for (int J = j*M ; J < j*M; J){
                    k += image[I][J];
                }
            }
            v[i][j] = k/N*M;
        }
    }

    //print it out
    for (int i = 0; i < 100; i++){
        for (int j = 0; j < 100; j++){
            cout << v[i][j] <<" ";
        }
    }

    return 0;
}