#include <iostream>
#include <vector>

using namespace std;
vector<int> image1(1e4,0);
vector<int> image2(1e4,0);


int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int DifferencePerPixel, DifferencePercent;
    cin >> DifferencePerPixel >> DifferencePercent;
    for (int i = 0; i < 1e4; i++) cin >> image1[i] >> image2[i];

    return 0;
}