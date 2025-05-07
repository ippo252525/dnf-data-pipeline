ENDPOINT_DEFINITIONS = {
    
    # 01. 서버 정보
    'server' : {
        'url' : 'https://api.neople.co.kr/df/servers?apikey={apikey}',
        'default_params' : {}
    },
    
    # 02. 캐릭터 검색
    'character_search' : {
        'url' : 'https://api.neople.co.kr/df/servers/{serverId}/characters?characterName={characterName}&jobId={jobId}&jobGrowId={jobGrowId}&isAllJobGrow={isAllJobGrow}&limit={limit}&wordType={wordType}&apikey={apikey}',
        'default_params' : {
            'jobId' : '', 
            'jobGrowId' : '',
            'isAllJobGrow' : 'false', 
            'wordType' : 'match', 
            'limit' : 1
        }
    },

    # 03. 캐릭터 기본정보 조회
    'character_info' : {
        'url' : 'https://api.neople.co.kr/df/servers/{serverId}/characters/{characterId}?apikey={apikey}',
        'default_params' : {}        
    },
    
    # 04. 캐릭터 타임라인 정보 조회
    'character_timeline' : {
        'url' : 'https://api.neople.co.kr/df/servers/{serverId}/characters/{characterId}/timeline?limit={limit}&code={code}&startDate={startDate}&endDate={endDate}&next={next}&apikey={apikey}',
        'default_params' : {
            'startDate' : '',
            'endDate' : '',
            'limit' : 100,
            'code' : '',
            'next' : ''
        }        
    },

    # 05. 캐릭터 능력치 정보 조회
    'character_status' : {
        'url' : 'https://api.neople.co.kr/df/servers/{serverId}/characters/{characterId}/status?apikey={apikey}',
        'default_params' : {}        
    },

    # 06. 캐릭터 장착 장비 조회
    'character_equipment' : {
        'url' : 'https://api.neople.co.kr/df/servers/{serverId}/characters/{characterId}/equip/equipment?apikey={apikey}',
        'default_params' : {}        
    },

    # 07. 캐릭터 장착 아바타 조회
    'character_avatar' : {
        'url' : 'https://api.neople.co.kr/df/servers/{serverId}/characters/{characterId}/equip/avatar?apikey={apikey}',
        'default_params' : {}        
    },

    # 08. 캐릭터 장착 크리쳐 조회
    'character_creature' : {
        'url' : 'https://api.neople.co.kr/df/servers/{serverId}/characters/{characterId}/equip/creature?apikey={apikey}',
        'default_params' : {}        
    },

    # 09. 캐릭터 장착 휘장 조회
    'character_flag' : {
        'url' : 'https://api.neople.co.kr/df/servers/{serverId}/characters/{characterId}/equip/flag?apikey={apikey}',
        'default_params' : {}        
    },

    # 10. 캐릭터 장착 탈리스만 조회
    'character_talisman' : {
        'url' : 'https://api.neople.co.kr/df/servers/{serverId}/characters/{characterId}/equip/talisman?apikey={apikey}',
        'default_params' : {}        
    },

    # 11. 캐릭터 스킬 스타일 조회
    'character_skill_style' : {
        'url' : 'https://api.neople.co.kr/df/servers/{serverId}/characters/{characterId}/skill/style?apikey={apikey}',
        'default_params' : {}        
    },

    # 12. 캐릭터 버프 스킬 강화 장착 장비 조회
    'character_buff_equipment' : {
        'url' : 'https://api.neople.co.kr/df/servers/{serverId}/characters/{characterId}/skill/buff/equip/equipment?apikey={apikey}',
        'default_params' : {}        
    },

    # 13. 캐릭터 버프 스킬 강화 장착 아바타 조회
    'character_buff_avatar' : {
        'url' : 'https://api.neople.co.kr/df/servers/{serverId}/characters/{characterId}/skill/buff/equip/avatar?apikey={apikey}',
        'default_params' : {}        
    },

    # 14. 캐릭터 버프 스킬 강화 장착 크리처 조회
    'character_buff_creature' : {
        'url' : 'https://api.neople.co.kr/df/servers/{serverId}/characters/{characterId}/skill/buff/equip/creature?apikey={apikey}',
        'default_params' : {}        
    },

    # 15. 캐릭터 명성 검색
    'character_fame' : {
        'url' : 'https://api.neople.co.kr/df/servers/{serverId}/characters-fame?minFame={minFame}&maxFame={maxFame}&jobId={jobId}&jobGrowId={jobGrowId}&isAllJobGrow={isAllJobGrow}&isBuff={isBuff}&limit={limit}&apikey={apikey}',
        'default_params' : {
            'serverId' : 'all',
            'minFame' : '',
            'maxFame' : '',
            'jobId' : '', 
            'jobGrowId' : '',
            'isAllJobGrow' : 'true',
            'isBuff' : '',
            'limit' : 200
        }        
    },

    # 32. 직업 정보
    'job_info' : {
        'url' : 'https://api.neople.co.kr/df/jobs?apikey={apikey}',
        'default_params' : {}
    }
}