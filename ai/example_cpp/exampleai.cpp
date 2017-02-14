#include "json/json.h"
#include <iostream>
#include <string>
#include <vector>
#include <cstring>
#include <ctime>
using namespace std;

class AI {
private:
    vector<int> cards;
    string name;
public:
    AI();
    bool ProcessInfo();
    void InfoSetup(Json::Value jsVal);
    void InfoNewGame(Json::Value jsVal);
    void InfoGame(Json::Value jsVal);
    void InfoMove(Json::Value jsVal);
    void InfoScore(Json::Value jsVal);
    void InfoGameEnd(Json::Value jsVal);
    int CmdPickCard();
    int CmdPickRow();
    void Send(string s);
    void Start();
    // Utilities 
    int RandRange(int a, int b);
};
AI::AI()
{
    srand(time(NULL));
}
void AI::InfoSetup(Json::Value jsVal)
{
    name = jsVal["name"].asString();
    return;
}
void AI::InfoNewGame(Json::Value jsVal)
{
    this->cards.clear();
    for (int i = 0; i < jsVal.size(); i++) {
        this->cards.push_back(jsVal[i].asInt());
    }
    return;
}
void AI::InfoGame(Json::Value jsVal)
{
    return;
}
void AI::InfoMove(Json::Value jsVal)
{
    return;
}
void AI::InfoScore(Json::Value jsVal)
{
    return;
}
void AI::InfoGameEnd(Json::Value jsVal)
{
    return;
}
int AI::CmdPickCard()
{
    int idx = RandRange(0, this->cards.size());
    int retCard = this->cards[idx];
    this->cards.erase(this->cards.begin()+idx);
    return retCard;
}
int AI::CmdPickRow()
{
    return RandRange(0,4);
}
bool AI::ProcessInfo()
{
    string line;
    char* cline = NULL;
    char* pch = NULL;
    vector<string> data;
    Json::Reader reader;

    getline(cin, line);
    if (line == "") {
        return false;
    }
    cline = new char[line.size()+1];
    strcpy(cline, line.c_str());
    pch = strtok(cline, "|");
    while (pch != NULL) {
        data.push_back(pch);
        pch = strtok(NULL, "|");
    } 
    delete []cline;

    if (data[0] == "INFO") {
        Json::Value jsVal;
        reader.parse(data[2], jsVal);
        if (data[1] == "SETUP") {
            InfoSetup(jsVal);
        } else if (data[1] == "NEWGAME") {
            InfoNewGame(jsVal);
        } else if (data[1] == "GAME") {
            InfoGame(jsVal);
        } else if (data[1] == "MOVE") {
            InfoMove(jsVal);
        } else if (data[1] == "SCORE") {
            InfoScore(jsVal);
        } else if (data[1] == "GAMEEND") {
            InfoGameEnd(jsVal);
            return false;
        }
    } else if (data[0] == "CMD") {
        if (data[1] == "PICKCARD") {
            Send(to_string(CmdPickCard()));
        } else if (data[1] == "PICKROW") {
            Send(to_string(CmdPickRow()));
        }
    }
    return true;

}
void AI::Send(string s)
{
    cout<<s<<endl;
}
void AI::Start()
{
    while (1) {
        if (!ProcessInfo()) {
            break;
        }
    }
}
int AI::RandRange(int a, int b)
{
    return a+rand()%(b-a);
}
int main()
{
    AI ai;
    ai.Start();
    return 0;
}
